import os

os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2, 40))
from typing import Any, List

import cv2
import numpy as np


def get_vertices(background_image: np.ndarray, epsilon_coefficient: float) -> List[np.ndarray]:
    thresholded = np.where(background_image == 1, 0, 255).astype(np.uint8)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        return get_vertices_from_contours(contours, epsilon_coefficient)
    else:
        raise Exception("No contours found.")


def get_vertices_from_contours(contours: Any, epsilon_coefficient: float) -> List[np.ndarray]:
    largest_contour = max(contours, key=cv2.contourArea)
    epsilon = epsilon_coefficient * cv2.arcLength(largest_contour, True)
    vertices = cv2.approxPolyDP(largest_contour, epsilon, True)
    vertices = list(map(lambda vertex: vertex[0], vertices))
    return vertices
