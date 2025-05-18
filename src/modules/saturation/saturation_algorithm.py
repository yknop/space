import cv2
import numpy as np

from db_connections.update_object import add_disruption
from db_connections.disruptions_enum import Disruptions
from utils.logger.write import logger
from utils.consts.consts_by_satellite_name import get_consts_saturation
from utils.polygon.polygon import create_polygon


def saturation_disruption(db, image_path, image_id, satellite_name, *args, **kwargs):
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


def saturation_check(image, satellite_name):
    consts = get_consts_saturation(satellite_name)
    saturated_pixels, saturated_squares = saturation_check_use_grid(image, consts)
    saturated_image = is_saturation_image(
        image, saturated_pixels, consts["disruption_percent"]
    )
    return saturated_image, saturated_squares


def saturation_check_use_grid(image, consts):
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


def saturated_square(image, x, y, saturated_squares, consts):
    square = image[y : y + consts["grid_size"], x : x + consts["grid_size"]]
    saturated_pixels = calculate_saturation(square, consts["threshold_value"])
    if percent(saturated_pixels, square.size / 3) >= consts["square_percent"]:
        saturated_squares.append(
            [(x, y), (x + consts["grid_size"], y + consts["grid_size"])]
        )
        return saturated_pixels
    return 0


def calculate_saturation(square, threshold_value):
    return np.sum(np.all(square > threshold_value, axis=-1))


def is_saturation_image(image, saturated_pixels, disruption_percent):
    total_pixels = image.size / 3
    saturation_percentage = percent(saturated_pixels, total_pixels)
    return saturation_percentage >= disruption_percent


def percent(value, total):
    if total == 0:
        return 0
    return (value / total) * 100
