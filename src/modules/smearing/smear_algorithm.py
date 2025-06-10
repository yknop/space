import os
from itertools import product
from typing import Any, Dict, List, Tuple

import cv2
import rasterio

from db_connections.disruptions_enum import Disruptions
from db_connections.update_object import add_disruption
from modules.smearing.check_smeared_image import compare_decay
from modules.smearing.check_smooth import is_smooth_region
from utils.consts.consts_by_satellite_name import get_consts_smear
from utils.files.manage_folders import create_folder, remove_file, remove_folder
from utils.images.image_background import is_background_sub_image
from utils.images.manage_sub_image import create_sub_image
from utils.logger.write import get_logger
from utils.polygon.polygon import create_polygon

logger = get_logger()


def smear_disruption(
    db: Any,
    image_path: str,
    image_id: Any,
    satellite_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    try:
        smeared_squares: List[List[Tuple[int, int]]] = []
        image_folder, file_name = os.path.split(image_path)
        image_name, extension = os.path.splitext(file_name)
        image = rasterio.open(image_path)
        width, height = image.width, image.height
        image.close()
        if is_smear_image(
            image_folder,
            image_name,
            extension,
            width,
            height,
            smeared_squares,
            satellite_name,
            kwargs["background_image"],
        ):
            polygon = create_polygon(smeared_squares)
            add_disruption(db, image_id, Disruptions.SMEAR.value, polygon)
        logger.info(f"Smear check passed successfully on {image_name}")
    except Exception:
        error_log = f"Failing to check smear in the {image_name}"
        logger.error(error_log, exc_info=True)


def is_smear_image(
    image_folder: str,
    image_name: str,
    extension: str,
    width: int,
    height: int,
    smeared_squares: List[List[Tuple[int, int]]],
    satellite_name: str,
    background_image: Any,
) -> bool:
    consts = get_consts_smear(satellite_name)
    create_folder(image_name)
    sum_smeared_pixels, sum_pixels = arrange_to_send_smear_test(
        consts,
        image_folder,
        image_name,
        extension,
        width,
        height,
        smeared_squares,
        background_image,
    )
    remove_folder(image_name)
    number_damaged_pixels = sum_smeared_pixels / sum_pixels * 100
    return number_damaged_pixels > consts["percentage_threshold_value"]


def arrange_to_send_smear_test(
    consts: Dict[str, float],
    image_folder: str,
    image_name: str,
    extension: str,
    width: int,
    height: int,
    smeared_squares: List[List[Tuple[int, int]]],
    background_image: Any,
) -> Tuple[int, int]:
    sum_pixels = 0
    sum_smeared_pixels = 0
    grid = product(range(0, width, consts["size"]), range(0, height, consts["size"]))
    for x, y in grid:
        sub_image_pixels, sub_image_smear_pixels = smear_sub_image_algorithm(
            image_folder,
            image_name,
            extension,
            width,
            height,
            x,
            y,
            smeared_squares,
            consts,
            background_image,
        )
        sum_pixels += sub_image_pixels
        sum_smeared_pixels += sub_image_smear_pixels
    return sum_smeared_pixels, sum_pixels


def smear_sub_image_algorithm(
    image_folder: str,
    image_name: str,
    extension: str,
    width: int,
    height: int,
    x: int,
    y: int,
    smeared_squares: List[List[Tuple[int, int]]],
    consts: Dict[str, float],
    background_image: Any,
) -> Tuple[int, int]:
    width_sub_image = min(x + consts["size"], width) - x
    height_sub_image = min(y + consts["size"], height) - y

    if is_background_sub_image(background_image, x, y, width_sub_image, height_sub_image):
        return 0, 0
    sub_image_path = create_sub_image(
        x,
        y,
        f"{image_name}{extension}",
        image_folder,
        width_sub_image,
        height_sub_image,
    )
    is_smeared = detect_smeared_image(sub_image_path, consts)
    remove_file(sub_image_path)
    if is_smeared:
        smeared_squares.append([(x, y), (x + width_sub_image, y + height_sub_image)])
        return width_sub_image * height_sub_image, width_sub_image * height_sub_image
    return width_sub_image * height_sub_image, 0


def detect_smeared_image(image_path: str, consts: Dict[str, float]) -> bool:
    image = cv2.imread(f"{image_path}", 0)
    decay = compare_decay(image)
    if (not decay) or is_smooth_region(image, consts):
        return False
    return decay < consts["threshold_value"]
