from typing import List, Tuple

from modules.cutting.parallel_lines import get_slope, are_parallel_lines


def is_dodecagon(
    vertices: List[Tuple[float, float]], slope_difference_threshold_value: float
) -> bool:
    if len(vertices) != 12:
        return False
    return check_are_all_lines_parallel_in_direction(
        vertices, slope_difference_threshold_value
    )


def check_are_all_lines_parallel_in_direction(
    vertices: List[Tuple[float, float]], slope_difference_threshold_value: float
) -> bool:
    indexes_direction_1 = [[x, x + 1] for x in range(0, 12, 2)]
    indexes_direction_2 = [[x, (x + 1) % 12] for x in range(1, 13, 2)]
    slopes_in_direction_1 = [
        get_slope(vertices[item[0]], vertices[item[1]]) for item in indexes_direction_1
    ]
    slopes_in_direction_2 = [
        get_slope(vertices[item[0]], vertices[item[1]]) for item in indexes_direction_2
    ]
    return are_all_lines_parallel(
        slopes_in_direction_1, slope_difference_threshold_value
    ) and are_all_lines_parallel(
        slopes_in_direction_2, slope_difference_threshold_value
    )


def are_all_lines_parallel(
    slopes: List[float], slope_difference_threshold_value: float
) -> bool:
    for index in range(len(slopes)):
        if not is_line_parallel_to_all_lines(
            slopes, index, slope_difference_threshold_value
        ):
            return False
    return True


def is_line_parallel_to_all_lines(
    slopes: List[float], index: int, slope_difference_threshold_value: float
) -> bool:
    for index2 in range(index + 1, len(slopes)):
        if not are_parallel_lines(
            slopes[index], slopes[index2], slope_difference_threshold_value
        ):
            return False
    return True
