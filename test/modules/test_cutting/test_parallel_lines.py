from unittest.mock import patch, call


from modules.cutting.parallel_lines import (
    get_slope,
    are_parallel_lines,
    check_are_parallel_vertical_lines,
)


def test_get_slope():
    assert get_slope([0, 0], [5, 5]) == 1
    assert get_slope([10, 0], [5, -1]) == 0.2
    assert get_slope([5, 5], [10, 0]) == -1
    assert get_slope([5, -1], [0, 0]) == -0.2


def test_get_slope_when_line_is_vertical():
    assert get_slope([4, 4], [4, 8]) == "vertical"


@patch(
    "modules.cutting.parallel_lines.check_are_parallel_vertical_lines",
    return_value="return from check_are_parallel_vertical_lines",
)
def test_are_parallel_lines(mock_check_are_parallel_vertical_lines):
    assert are_parallel_lines(0.03, 0.1, 0.25)
    assert not are_parallel_lines(0.3, 0.01, 0.25)
    mock_check_are_parallel_vertical_lines.assert_not_called()


@patch(
    "modules.cutting.parallel_lines.check_are_parallel_vertical_lines",
    return_value="return from check_are_parallel_vertical_lines",
)
def test_are_parallel_lines_when_at_least_one_slope_is_vertical(
    mock_check_are_parallel_vertical_lines,
):
    assert (
        are_parallel_lines("vertical", 5, 0.25)
        == "return from check_are_parallel_vertical_lines"
    )
    assert (
        are_parallel_lines("vertical", "vertical", 0.25)
        == "return from check_are_parallel_vertical_lines"
    )
    assert (
        are_parallel_lines(2, "vertical", 0.25)
        == "return from check_are_parallel_vertical_lines"
    )
    assert mock_check_are_parallel_vertical_lines.call_count == 3
    mock_check_are_parallel_vertical_lines.assert_has_calls(
        [
            call("vertical", 5, 0.25),
            call("vertical", "vertical", 0.25),
            call(2, "vertical", 0.25),
        ]
    )


def test_check_are_parallel_vertical_lines():
    assert check_are_parallel_vertical_lines("vertical", "vertical", 0.25)
    assert check_are_parallel_vertical_lines("vertical", 10, 0.25)
    assert check_are_parallel_vertical_lines(10, "vertical", 0.25)
    assert not check_are_parallel_vertical_lines("vertical", 3, 0.25)
    assert not check_are_parallel_vertical_lines(3, "vertical", 0.25)
