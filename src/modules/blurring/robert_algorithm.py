import cv2
import numpy as np
from typing import List

from modules.blurring.is_blur import decide_if_blur


def robert_data(image: np.ndarray, threshold_values: List[float]) -> int:
    kernel_x = np.array([[1, 0], [0, -1]])
    kernel_y = np.array([[0, 1], [-1, 0]])
    gradient_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    gradient_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    robert_result = np.sqrt(gradient_x**2 + gradient_y**2)
    maximum = np.max(robert_result)
    average = np.mean(robert_result)
    variance = np.var(robert_result)
    return decide_if_blur(maximum, average, variance, threshold_values)
