from typing import Any, Dict, List, Tuple, Union

import cv2
import numpy as np
from bson.objectid import ObjectId
from pymongo.database import Database

from db_connections.disruptions_enum import Disruptions
from db_connections.update_object import add_disruption
from utils.consts.consts_by_satellite_name import get_consts_saturation
from utils.logger.write import get_logger
from utils.polygon.polygon import create_polygon

logger = get_logger()


def saturation_disruption(
    db: Database,
    image_path: str,
    image_id: ObjectId,
    satellite_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    logger.info(f"Start saturation")
    try:
        image = cv2.imread(image_path)
        saturated_image, saturated_squares = saturation_check(image, satellite_name)
        if saturated_image:
            polygon = create_polygon(saturated_squares)
            add_disruption(db, image_id, Disruptions.SATURATION.value, polygon)
        logger.info(f"Saturation check passed successfully on {image_path}")
    except Exception:
        error_log = f"Failing to check saturation in the {image_path}"
        logger.error(error_log, exc_info=True)


def saturation_check(
    image: np.ndarray, satellite_name: str
) -> Tuple[bool, List[List[Tuple[int, int]]]]:
    consts = get_consts_saturation(satellite_name)
    saturated_pixels, saturated_squares = saturation_check_use_grid(image, consts)
    saturated_image = is_saturation_image(image, saturated_pixels, consts["disruption_percent"])
    return saturated_image, saturated_squares


def saturation_check_use_grid(
    image: np.ndarray, consts: Dict[str, Union[int, float]]
) -> Tuple[int, List[List[Tuple[int, int]]]]:
    height, width, _ = image.shape
    sum_saturated_pixels = 0
    saturated_squares = []
    coordinates = (
        (x, y)
        for y in range(0, height, consts["grid_size"])
        for x in range(0, width, consts["grid_size"])
    )
    for x, y in coordinates:
        sum_saturated_pixels += saturated_square(image, x, y, saturated_squares, consts)
    return sum_saturated_pixels, saturated_squares


def saturated_square(
    image: np.ndarray,
    x: int,
    y: int,
    saturated_squares: List[List[Tuple[int, int]]],
    consts: Dict[str, int],
) -> int:
    square = image[y : y + consts["grid_size"], x : x + consts["grid_size"]]
    saturated_pixels = calculate_saturation(square, consts["threshold_value"])
    if percent(saturated_pixels, square.size / 3) >= consts["square_percent"]:
        saturated_squares.append([(x, y), (x + consts["grid_size"], y + consts["grid_size"])])
        return saturated_pixels
    return 0


def calculate_saturation(square: np.ndarray, threshold_value: Union[int, float]) -> int:
    return np.sum(np.all(square > threshold_value, axis=-1))


def is_saturation_image(image: np.ndarray, saturated_pixels: int, disruption_percent: int) -> bool:
    total_pixels = image.size / 3
    saturation_percentage = percent(saturated_pixels, total_pixels)
    return saturation_percentage >= disruption_percent


def percent(value: Union[int, float], total: Union[int, float]) -> float:
    if total == 0:
        return 0
    return (value / total) * 100
