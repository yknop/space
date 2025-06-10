from typing import Union

import cv2
import numpy as np

from consts.smear import BLOCK_SIZE, COORDINATES_OF_BLOCK
from consts.smear import DECAY_FACTOR as decay_factor


def compare_decay(image: np.ndarray) -> None:
    general_spectrogram_decay = general_decay(image)
    block_spectrogram_decay = block_decay(image, general_spectrogram_decay)
    if not isinstance(block_spectrogram_decay, np.ndarray):
        return None
    decay_ratio = np.mean(np.abs(general_spectrogram_decay - block_spectrogram_decay))
    return decay_ratio


def general_decay(image: np.ndarray) -> np.ndarray:
    spectrogram = spectrogram_FFT(image)
    decay = vertical_decay(spectrogram)
    return decay


def spectrogram_FFT(image: np.ndarray) -> np.ndarray:
    return np.abs(np.fft.fftshift(np.fft.fft2(image)))


def vertical_decay(spectrogram: np.ndarray) -> np.ndarray:
    rows, cols = spectrogram.shape
    vertical_frequencies = np.fft.fftfreq(rows).reshape(-1, 1)
    horizontal_frequencies = np.fft.fftfreq(cols).reshape(1, -1)
    vertical_decay = 1 / (1 + decay_factor * (vertical_frequencies**2))
    horizontal_decay = 1 / (1 + decay_factor * (horizontal_frequencies**2))
    total_decay = vertical_decay * horizontal_decay
    return spectrogram * total_decay


def block_decay(image: np.ndarray, general_spectrogram: np.ndarray) -> Union[int, np.ndarray]:
    x, y = COORDINATES_OF_BLOCK
    block = image[y : y + BLOCK_SIZE[1], x : x + BLOCK_SIZE[0]]
    if block.shape[0] == 0:
        return 0
    spectrogram = spectrogram_FFT(block)
    resized_spectrogram = cv2.resize(spectrogram, general_spectrogram.shape[::-1])
    decay = vertical_decay(resized_spectrogram)
    return decay
