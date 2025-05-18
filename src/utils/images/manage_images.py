import os
import cv2
import rasterio
import numpy as np
from rasterio.windows import Window
from typing import Tuple, Dict, Any, List

from utils.images.convert_ntf import convert_image_to_8_bit, convert_ntf_to_tif
from utils.logger.write import logger
from utils.files.manage_folders import remove_file, get_ntf_file_and_folder_path


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


def create_background_image(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    width = len(image[0])
    height = len(image)
    background_image = np.zeros((height, width))
    fill_background_pixels(image, background_image)
    return background_image


def fill_background_pixels(image: np.ndarray, background_image: np.ndarray) -> None:
    background_pixels: List[Tuple[int, int]] = []
    for i in range(len(image)):
        fill_background_pixel(image, background_image, background_pixels, i, 0)
        fill_background_pixel(
            image, background_image, background_pixels, i, len(image[0]) - 1
        )
    for j in range(len(image[0])):
        fill_background_pixel(image, background_image, background_pixels, 0, j)
        fill_background_pixel(
            image, background_image, background_pixels, len(image) - 1, j
        )


def fill_background_pixel(
    image: np.ndarray,
    background_image: np.ndarray,
    background_pixels: List[Tuple[int, int]],
    i: int,
    j: int,
) -> None:
    if image[i][j] == 0 and background_image[i][j] != 1:
        background_pixels.append((i, j))
        change_background_pixels(image, background_image, background_pixels)


def change_background_pixels(
    image: np.ndarray,
    background_image: np.ndarray,
    background_pixels: List[Tuple[int, int]],
) -> None:
    while len(background_pixels):
        i, j = background_pixels.pop()
        if background_image[i][j] != 1:
            background_image[i][j] = 1
            change_pixel(image, background_image, background_pixels, i, j - 1)
            change_pixel(image, background_image, background_pixels, i, j + 1)
            change_pixel(image, background_image, background_pixels, i - 1, j)
            change_pixel(image, background_image, background_pixels, i + 1, j)


def change_pixel(
    image: np.ndarray,
    background_image: np.ndarray,
    background_pixels: List[Tuple[int, int]],
    i: int,
    j: int,
) -> None:
    if (
        is_correct_position(background_image, i, j)
        and image[i][j] == 0
        and background_image[i][j] != 1
    ):
        background_pixels.append((i, j))


def is_correct_position(background_image: np.ndarray, i: int, j: int) -> bool:
    return (
        i >= 0 and i < len(background_image) and j >= 0 and j < len(background_image[0])
    )


def is_background_sub_image(
    background_image: np.ndarray,
    x: int,
    y: int,
    width_sub_image: int,
    height_sub_image: int,
) -> bool:
    for i in range(x, x + width_sub_image):
        for j in range(y, y + height_sub_image):
            if background_image[j][i] == 1:
                return True
    return False
