from typing import List

import cv2
import numpy as np

from modules.blurring.is_blur import decide_if_blur


def sobel_data(image: np.ndarray, threshold_values: List[float]) -> int:
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1)
    sobel_result = np.sqrt(sobelx**2 + sobely**2)
    maximum = np.max(sobel_result)
    average = np.mean(sobel_result)
    variance = np.var(sobel_result)
    return decide_if_blur(maximum, average, variance, threshold_values)
