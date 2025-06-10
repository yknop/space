from typing import Tuple, Union


def get_slope(point1: Tuple[float, float], point2: Tuple[float, float]) -> Union[float, str]:
    if (point1[0] - point2[0]) == 0:
        return "vertical"
    return (point1[1] - point2[1]) / (point1[0] - point2[0])


def are_parallel_lines(
    slope1: Union[float, str],
    slope2: Union[float, str],
    slope_difference_threshold_value: float,
) -> bool:
    if isinstance(slope1, str) or isinstance(slope2, str):
        return are_parallel_vertical_lines(slope1, slope2, slope_difference_threshold_value)
    return abs(slope1 - slope2) < slope_difference_threshold_value


def are_parallel_vertical_lines(
    slope1: Union[float, str],
    slope2: Union[float, str],
    slope_difference_threshold_value: float,
) -> bool:
    if slope1 == slope2:
        return True
    another_slope = slope1 if slope2 == "vertical" else slope2
    inverse_slope = 1 / slope_difference_threshold_value
    return abs(another_slope) > inverse_slope
