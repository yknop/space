import cv2
import numpy as np
from typing import List

from modules.blurring.is_blur import decide_if_blur


def laplacian_data(image: np.ndarray, threshold_values: List[float]) -> int:
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    laplacian = np.uint8(np.absolute(laplacian))
    maximum = np.max(laplacian)
    average = np.mean(laplacian)
    variance = np.var(laplacian)
    return decide_if_blur(maximum, average, variance, threshold_values)
