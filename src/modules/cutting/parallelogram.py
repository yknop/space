from typing import List, Tuple

from modules.cutting.parallel_lines import are_parallel_lines, get_slope


def is_parallelogram(
    vertices: List[Tuple[float, float]], slope_difference_threshold_value: float
) -> bool:
    if len(vertices) != 4:
        return False
    return are_parallel_lines(
        get_slope(vertices[0], vertices[1]),
        get_slope(vertices[2], vertices[3]),
        slope_difference_threshold_value,
    ) and are_parallel_lines(
        get_slope(vertices[1], vertices[2]),
        get_slope(vertices[3], vertices[0]),
        slope_difference_threshold_value,
    )
