from typing import List


def decide_if_blur(
    maximum: float, average: float, variance: float, threshold_values: List[float]
) -> int:
    if variance == 0:
        return 0
    value = ((maximum - average) / variance) * 1000
    if value < threshold_values[0]:
        return -1
    elif value < threshold_values[1]:
        return 0
    elif value < threshold_values[2]:
        return 1
    else:
        return 2
