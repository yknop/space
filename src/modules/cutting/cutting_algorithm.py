from typing import Any, Dict

import numpy as np

from db_connections.disruptions_enum import Disruptions
from db_connections.update_object import add_disruption
from modules.cutting.dodecagon import is_dodecagon
from modules.cutting.parallelogram import is_parallelogram
from modules.cutting.vertices import get_vertices
from utils.consts.consts_by_satellite_name import get_consts_cutting_image
from utils.files.extract_value import get_value_by_keys
from utils.logger.write import get_logger

logger = get_logger()


def cutting_disruption(
    db: Any,
    image_path: str,
    image_id: str,
    satellite_name: str,
    json_file_path: str,
    shape: str,
    *args: Any,
    **kwargs: Dict[str, Any],
) -> None:
    try:
        consts = get_consts_cutting_image(satellite_name)
        if is_cut(kwargs["background_mask"], json_file_path, shape, consts):
            add_disruption(db, image_id, Disruptions.CUT_IMAGE.value)
        logger.info(f"Cutting check passed successfully on {image_path}")
    except Exception:
        error_log = f"Failing to check cutting in the {image_path}"
        logger.error(error_log, exc_info=True)


def is_cut(
    background_mask: np.ndarray, json_file_path: str, shape: str, consts: Dict[str, Any]
) -> bool:
    if is_not_polygon(json_file_path):
        return True
    vertices = get_vertices(background_mask, consts["epsilon_coefficient"])
    match shape:
        case "parallelogram":
            return not is_parallelogram(vertices, consts["slope_difference_threshold_value"])
        case "dodecagon":
            return not is_dodecagon(vertices, consts["slope_difference_threshold_value"])
        case _:
            raise ValueError(f"The shape: {shape} is not supported.")


def is_not_polygon(json_file_path: str) -> bool:
    try:
        type_shape = get_value_by_keys(json_file_path, ["geometry", "type"])
        return type_shape != "Polygon"
    except Exception as error:
        raise Exception(f"When trying to read from metadata.json an error occurred: {error}")
