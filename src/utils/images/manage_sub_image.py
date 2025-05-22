import os
import numpy as np
import rasterio
from rasterio.windows import Window
from typing import Any, Dict, Tuple

from utils.logger.write import logger


def save_sub_image(
    sub_image_path: str, sub_image: np.ndarray, profile_sub_image: Dict[str, Any]
) -> None:
    try:
        dest_image = rasterio.open(sub_image_path, "w", **profile_sub_image)
        dest_image.write(sub_image)
        dest_image.close()
    except Exception as error:
        error_log = "An error occured when write sub image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def create_sub_image(
    x: int, y: int, file_name: str, img_dir: str, width_size: int, height_size: int
) -> str:
    try:
        name, _ = os.path.splitext(file_name)
        img_path = os.path.join(img_dir, file_name)
        sub_image_path = os.path.join(f"{name}", f"{name}_{x}_{y}.tif")
        sub_image, profile_sub_image = read_sub_image(
            img_path, x, y, width_size, height_size
        )
        save_sub_image(sub_image_path, sub_image, profile_sub_image)
        return sub_image_path
    except Exception as error:
        error_log = "An error occured in create_sub_image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def read_sub_image(
    img_path: str, x: int, y: int, width_size: int, height_size: int
) -> Tuple[np.ndarray, Dict[str, Any]]:
    try:
        window = Window(x, y, width_size, height_size)
        src_image = rasterio.open(img_path)
        sub_image = src_image.read(window=window)
        new_profile = get_new_profile(
            src_image.profile.copy(),
            width_size,
            height_size,
            window,
            src_image.transform,
        )
        src_image.close()
        return sub_image, new_profile
    except Exception as error:
        error_log = "An error occured when read sub image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def get_new_profile(
    profile: Dict[str, Any],
    width_size: int,
    height_size: int,
    window: Window,
    transform: Any,
) -> Dict[str, Any]:
    profile.update(
        {
            "driver": "GTiff",
            "height": height_size,
            "width": width_size,
            "transform": rasterio.windows.transform(window, transform),
        }
    )
    return profile
