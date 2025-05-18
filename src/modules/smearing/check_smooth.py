import cv2
import numpy as np
from typing import Dict


def is_smooth_region(image: np.ndarray, consts: Dict[str, float]) -> bool:
    sobel_value = gradient_energy(image)

    if sobel_value < consts["sobel_value"]:
        return True

    if sobel_value > consts["sobel_value"] * 2:
        return False

    laplacian_value = variance_of_laplacian(image)
    blur_diff = gaussian_blur_difference(image)

    if laplacian_value < consts["laplacian_value"] and blur_diff < consts["blur_value"]:
        return True

    if laplacian_value > consts["laplacian_value"] and blur_diff > consts["blur_value"]:
        return False

    return blur_diff < consts["blur_value"]


def gradient_energy(image: np.ndarray) -> float:
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    return np.mean(np.abs(grad_x)) + np.mean(np.abs(grad_y))


def variance_of_laplacian(image: np.ndarray) -> float:
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    return laplacian.var()


def gaussian_blur_difference(image: np.ndarray) -> float:
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    diff = np.abs(image.astype(np.float32) - blurred.astype(np.float32))
    return np.mean(diff)
