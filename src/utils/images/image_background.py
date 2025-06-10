from typing import List, Tuple

import cv2
import numpy as np


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
        fill_background_pixel(image, background_image, background_pixels, i, len(image[0]) - 1)
    for j in range(len(image[0])):
        fill_background_pixel(image, background_image, background_pixels, 0, j)
        fill_background_pixel(image, background_image, background_pixels, len(image) - 1, j)


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
    return i >= 0 and i < len(background_image) and j >= 0 and j < len(background_image[0])
