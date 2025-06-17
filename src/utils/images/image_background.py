from collections import deque
from typing import Deque, Tuple

import numpy as np


def is_background_sub_image(
    background_mask: np.ndarray,
    x: int,
    y: int,
    width_sub_image: int,
    height_sub_image: int,
) -> bool:
    sub = background_mask[y : y + height_sub_image, x : x + width_sub_image]
    return np.any(sub)


def create_background_image(image: np.ndarray) -> np.ndarray:
    background_mask = np.zeros_like(image, dtype=np.uint8)
    queue: Deque[Tuple[int, int]] = deque()

    add_border_background_pixels(image, background_mask, queue)
    flood_fill_background(image, background_mask, queue)

    return background_mask


def add_border_background_pixels(
    image: np.ndarray,
    background_mask: np.ndarray,
    queue: Deque[Tuple[int, int]],
) -> None:
    height, width = image.shape

    for i in range(height):
        for j in [0, width - 1]:
            add_background_pixel_if_needed(image, background_mask, queue, i, j)

    for j in range(1, width - 1):
        for i in [0, height - 1]:
            add_background_pixel_if_needed(image, background_mask, queue, i, j)


def add_background_pixel_if_needed(
    image: np.ndarray,
    background_mask: np.ndarray,
    queue: Deque[Tuple[int, int]],
    i: int,
    j: int,
) -> None:
    if image[i, j] == 0 and not background_mask[i, j]:
        background_mask[i, j] = True
        queue.append((i, j))


def flood_fill_background(
    image: np.ndarray,
    background_mask: np.ndarray,
    queue: Deque[Tuple[int, int]],
) -> None:
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        i, j = queue.popleft()
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if is_valid_background_pixel(image, background_mask, ni, nj):
                background_mask[ni, nj] = True
                queue.append((ni, nj))


def is_valid_background_pixel(
    image: np.ndarray,
    background_mask: np.ndarray,
    i: int,
    j: int,
) -> bool:
    return (
        0 <= i < image.shape[0]
        and 0 <= j < image.shape[1]
        and image[i, j] == 0
        and not background_mask[i, j]
    )
