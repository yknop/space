import os
from itertools import product
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import rasterio

from db_connections.disruptions_enum import Disruptions
from db_connections.update_object import add_disruption
from modules.blurring.laplacian_algorithm import laplacian_data
from modules.blurring.robert_algorithm import robert_data
from modules.blurring.sobel_algorithm import sobel_data
from utils.consts.consts_by_satellite_name import get_consts_blur
from utils.images.image_background import is_background_sub_image
from utils.images.manage_sub_image import extract_sub_image_array
from utils.logger.write import get_logger
from utils.polygon.polygon import create_polygon

logger = get_logger()


def blur_disruption(
    db: Any,
    image_path: str,
    image_id: str,
    satellite_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    try:
        blurred_squares: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        image_folder, file_name = os.path.split(image_path)
        image_name, extension = os.path.splitext(file_name)
        image = rasterio.open(image_path)
        width, height = image.width, image.height
        image.close()
        if is_blur_image(
            image_folder,
            image_name,
            extension,
            width,
            height,
            blurred_squares,
            satellite_name,
            kwargs["background_mask"],
        ):
            polygon = create_polygon(blurred_squares)
            add_disruption(db, image_id, Disruptions.BLUR.value, polygon)
        logger.info(f"Blur check passed successfully on {image_path}")
    except Exception:
        error_log = f"Failing to check blur in the {image_path}"
        logger.error(error_log, exc_info=True)


def is_blur_image(
    image_folder: str,
    image_name: str,
    extension: str,
    width: int,
    height: int,
    blurred_squares: List[Tuple[Tuple[int, int], Tuple[int, int]]],
    satellite_name: str,
    background_mask: np.ndarray,
) -> bool:
    sum_pixels = 0
    sum_blurred_pixels = 0
    consts = get_consts_blur(satellite_name)
    image_path = os.path.join(image_folder, f"{image_name}{extension}")
    grid = product(
        range(0, width, consts["sub_image_size"]),
        range(0, height, consts["sub_image_size"]),
    )
    for x, y in grid:
        sub_image_pixels, sub_image_blur_pixels = blur_sub_image_algorithm(
            image_path,
            width,
            height,
            x,
            y,
            blurred_squares,
            consts,
            background_mask,
        )
        sum_pixels += sub_image_pixels
        sum_blurred_pixels += sub_image_blur_pixels

        if (
            sum_pixels > 0
            and (sum_blurred_pixels / sum_pixels * 100) > consts["percentage_threshold_value"]
        ):
            return True

    number_damaged_pixels = sum_blurred_pixels / sum_pixels * 100
    return number_damaged_pixels > consts["percentage_threshold_value"]


def blur_sub_image_algorithm(
    image_path: str,
    width: int,
    height: int,
    x: int,
    y: int,
    blurred_squares: List[Tuple[Tuple[int, int], Tuple[int, int]]],
    consts: dict,
    background_mask: np.ndarray,
) -> Tuple[int, int]:
    width_sub_image = min(x + consts["sub_image_size"], width) - x
    height_sub_image = min(y + consts["sub_image_size"], height) - y
    if is_background_sub_image(background_mask, x, y, width_sub_image, height_sub_image):
        return 0, 0
    sub_image = extract_sub_image_array(
        image_path,
        x,
        y,
        width_sub_image,
        height_sub_image,
    )
    gray_image = cv2.cvtColor(sub_image, cv2.COLOR_RGB2GRAY)
    is_blurred = detect_blurred_image(gray_image, consts)
    if is_blurred:
        blurred_squares.append([(x, y), (x + width_sub_image, y + height_sub_image)])
        return width_sub_image * height_sub_image, width_sub_image * height_sub_image
    return width_sub_image * height_sub_image, 0


def detect_blurred_image(image: np.ndarray, consts: Dict[str, float]) -> bool:
    blurred_laplacian = laplacian_data(image, consts["laplacian_threshold_values"])
    blurred_robert = robert_data(image, consts["robert_threshold_values"])
    blurred_sobel = sobel_data(image, consts["sobel_threshold_values"])
    return (blurred_laplacian + blurred_robert + blurred_sobel) > 1
