import os
import re
from typing import Any, Dict, Tuple

import cv2
import numpy as np
from bson.objectid import ObjectId
from pymongo.database import Database

from db_connections.update_object import add_end_date_value
from modules.blurring.blur_algorithm import blur_disruption
from modules.cutting.cutting_algorithm import cutting_disruption
from modules.saturation.saturation_algorithm import saturation_disruption
from modules.smearing.smear_algorithm import smear_disruption
from utils.consts.consts_by_satellite_name import get_satellite_details
from utils.files.extract_value import get_company_by_folder_name
from utils.files.manage_folders import (
    get_metadata_json_file,
    get_ntf_file_and_folder_path,
    remove_file,
)
from utils.images.convert_image import convert_image_to_8_bit, convert_ntf_to_tif
from utils.images.image_background import create_background_image
from utils.images.insert_image import insert_image_to_mongo
from utils.logger.write import get_logger

logger = get_logger()


def get_image_file(folder_path: str, satellite_name: str) -> Tuple[str, str]:
    match satellite_name:
        case "BlackSky":
            return convert_ntf_image(folder_path)
        case _:
            raise Exception("Unsupported satellite name.")


def convert_ntf_image(folder_path: str) -> Tuple[str, str]:
    try:
        input_ntf_image, folder_path = get_ntf_file_and_folder_path(folder_path)
        image_name = os.path.splitext(input_ntf_image)[0]
        if "pregeoreferenced" in image_name:
            logger.info(f"Ignoring non-ortho image: {image_name}")
        else:
            temp_tif_image = os.path.join(folder_path, f"{image_name}-temp.tif")
            output_tif_image = os.path.join(folder_path, f"{image_name}.tif")
            convert_ntf_to_tif(os.path.join(folder_path, input_ntf_image), temp_tif_image)
            convert_image_to_8_bit(temp_tif_image, output_tif_image)
            remove_file(temp_tif_image)
            return f"{image_name}.tif", output_tif_image
    except Exception as error:
        error_log = "Failed to convert ntf image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def get_image_data(path_image: str) -> Tuple[str, str, str, str, Dict[str, Any]]:
    try:
        json_file_path = get_metadata_json_file(path_image)
        satellite_name = get_company_by_folder_name(re.search(r"[^/\\]+$", path_image).group(0))
        tiff_file, image_path = get_image_file(path_image, satellite_name)
        satellite_details = get_satellite_details(satellite_name)
        tiff_file_name = os.path.splitext(tiff_file)[0]
        return (
            json_file_path,
            tiff_file_name,
            image_path,
            satellite_name,
            satellite_details,
        )
    except Exception as error:
        error_log = "An error occurred when writing sub image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def check_image(db: Database, path_image: str) -> None:
    try:
        (
            json_file_path,
            tiff_file_name,
            image_path,
            satellite_name,
            satellite_details,
        ) = get_image_data(path_image)
        logger.info("After   --get_image_data--   function")
        mongo_image_id: ObjectId = insert_image_to_mongo(
            db,
            tiff_file_name,
            json_file_path,
            satellite_details["date_location"],
            satellite_name,
        )
        logger.info("After   --insert_image_to_mongo--   function")
    except Exception:
        return
    send_to_check_disruptions(
        db,
        image_path,
        mongo_image_id,
        satellite_name,
        json_file_path,
        satellite_details["image_shape"],
    )
    add_end_date_value(db, mongo_image_id)


def send_to_check_disruptions(
    db: Database,
    image_path: str,
    mongo_image_id: ObjectId,
    satellite_name: str,
    json_file_path: str,
    image_shape: Any,
) -> None:
    image = load_image(image_path)
    background_mask = create_background_image(image) == 1
    for disruption in [
        blur_disruption,
        smear_disruption,
        saturation_disruption,
        cutting_disruption,
    ]:
        try:
            disruption(
                db,
                image_path,
                mongo_image_id,
                satellite_name,
                json_file_path,
                image_shape,
                background_mask=background_mask,
            )
        except Exception:
            continue


def load_image(image_path: str) -> np.ndarray:
    logger.info(f"Start load_image ----------")
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            return image
        logger.info(f"Image shape: {image.shape}, dtype: {image.dtype}")
    except Exception as error:
        error_log = "Failed to load image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
    return image
