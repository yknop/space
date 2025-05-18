from unittest.mock import patch, call

from modules.cutting.dodecagon import (
    is_dodecagon,
    check_are_all_lines_parallel_in_direction,
    are_all_lines_parallel,
    is_line_parallel_to_all_lines,
)


@patch(
    "modules.cutting.dodecagon.check_are_all_lines_parallel_in_direction",
    return_value="return from check_are_all_lines_parallel_in_direction",
)
def test_is_dodecagon_when_len_vertices_is_12(
    mock_check_are_all_lines_parallel_in_direction,
):
    assert (
        is_dodecagon(
            [
                [0, 0],
                [3, 3],
                [0, 4],
                [5, 12],
                [8, 10],
                [6, 8],
                [8, 6],
                [10, 8],
                [12, 7],
                [9, 1],
                [6, 2],
                [3, -1],
            ],
            0.25,
        )
        == "return from check_are_all_lines_parallel_in_direction"
    )
    mock_check_are_all_lines_parallel_in_direction.assert_called_once_with(
        [
            [0, 0],
            [3, 3],
            [0, 4],
            [5, 12],
            [8, 10],
            [6, 8],
            [8, 6],
            [10, 8],
            [12, 7],
            [9, 1],
            [6, 2],
            [3, -1],
        ],
        0.25,
    )


@patch(
    "modules.cutting.dodecagon.check_are_all_lines_parallel_in_direction",
    return_value="return from check_are_all_lines_parallel_in_direction",
)
def test_is_dodecagon_when_len_vertices_is_not_12(
    mock_check_are_all_lines_parallel_in_direction,
):
    assert not is_dodecagon([[0, 0], [3, 2], [5, 4]], 0.25)
    mock_check_are_all_lines_parallel_in_direction.assert_not_called()


@patch(
    "modules.cutting.dodecagon.get_slope",
    side_effect=[0.1, 0.11, 0.034, 0.06, 0.13, 0.28, -4, -5, -6.1, -4.5, -4.6, -5.5],
)
@patch("modules.cutting.dodecagon.are_all_lines_parallel", side_effect=[True, True])
def test_check_are_all_lines_parallel_in_direction_when_parallel(
    mock_are_all_lines_parallel, mock_get_slope
):
    assert check_are_all_lines_parallel_in_direction(
        [
            [0, 0],
            [1, 0],
            [0, 4],
            [5, 12],
            [8, 10],
            [6, 8],
            [8, 6],
            [10, 8],
            [12, 7],
            [9, 1],
            [6, 2],
            [3, -1],
        ],
        0.25,
    )
    assert mock_get_slope.call_count == 12
    mock_get_slope.assert_has_calls(
        [
            call([0, 0], [1, 0]),
            call([0, 4], [5, 12]),
            call([8, 10], [6, 8]),
            call([8, 6], [10, 8]),
            call([12, 7], [9, 1]),
            call([6, 2], [3, -1]),
            call([1, 0], [0, 4]),
            call([5, 12], [8, 10]),
            call([6, 8], [8, 6]),
            call([10, 8], [12, 7]),
            call([9, 1], [6, 2]),
            call([3, -1], [0, 0]),
        ]
    )
    assert mock_are_all_lines_parallel.call_count == 2
    mock_are_all_lines_parallel.assert_has_calls(
        [
            call([0.1, 0.11, 0.034, 0.06, 0.13, 0.28], 0.25),
            call([-4, -5, -6.1, -4.5, -4.6, -5.5], 0.25),
        ]
    )


@patch(
    "modules.cutting.dodecagon.get_slope",
    side_effect=[0.1, 0.11, 0.034, 0.06, 0.13, 0.28, -4, -5, -6.7, -4.5, -4.6, -5.5],
)
@patch(
    "modules.cutting.dodecagon.are_all_lines_parallel",
    side_effect=[True, False],
)
def test_check_are_all_lines_parallel_in_direction_when_not_parallel(
    mock_are_all_lines_parallel, mock_get_slope
):
    assert not check_are_all_lines_parallel_in_direction(
        [
            [0, 0],
            [1, 0],
            [0, 4],
            [5, 12],
            [8, 10],
            [6, 8],
            [8, 6],
            [10, 8],
            [12, 7],
            [9, 1],
            [6, 2],
            [3, -1],
        ],
        0.25,
    )
    assert mock_get_slope.call_count == 12
    mock_get_slope.assert_has_calls(
        [
            call([0, 0], [1, 0]),
            call([0, 4], [5, 12]),
            call([8, 10], [6, 8]),
            call([8, 6], [10, 8]),
            call([12, 7], [9, 1]),
            call([6, 2], [3, -1]),
            call([1, 0], [0, 4]),
            call([5, 12], [8, 10]),
            call([6, 8], [8, 6]),
            call([10, 8], [12, 7]),
            call([9, 1], [6, 2]),
            call([3, -1], [0, 0]),
        ]
    )
    assert mock_are_all_lines_parallel.call_count == 2
    mock_are_all_lines_parallel.assert_has_calls(
        [
            call([0.1, 0.11, 0.034, 0.06, 0.13, 0.28], 0.25),
            call([-4, -5, -6.7, -4.5, -4.6, -5.5], 0.25),
        ]
    )


@patch(
    "modules.cutting.dodecagon.is_line_parallel_to_all_lines",
    side_effect=[True, True, True, True, True],
)
def test_are_all_lines_parallel_when_all_lines_parallel(
    mock_is_line_parallel_to_all_lines,
):
    assert are_all_lines_parallel([0.05, 0.048, 0.03, 0.06, 0.07], 0.25)
    assert mock_is_line_parallel_to_all_lines.call_count == 5
    mock_is_line_parallel_to_all_lines.assert_has_calls(
        [
            call([0.05, 0.048, 0.03, 0.06, 0.07], 0, 0.25),
            call([0.05, 0.048, 0.03, 0.06, 0.07], 1, 0.25),
            call([0.05, 0.048, 0.03, 0.06, 0.07], 2, 0.25),
            call([0.05, 0.048, 0.03, 0.06, 0.07], 3, 0.25),
            call([0.05, 0.048, 0.03, 0.06, 0.07], 4, 0.25),
        ]
    )


@patch(
    "modules.cutting.dodecagon.is_line_parallel_to_all_lines",
    side_effect=[True, True, False, False, False],
)
def test_are_all_lines_parallel_when_not_parallel(mock_is_line_parallel_to_all_lines):
    assert not are_all_lines_parallel([0.5, 0.48, 0.3, 0.6, 0.7], 0.25)
    assert mock_is_line_parallel_to_all_lines.call_count == 3
    mock_is_line_parallel_to_all_lines.assert_has_calls(
        [
            call([0.5, 0.48, 0.3, 0.6, 0.7], 0, 0.25),
            call([0.5, 0.48, 0.3, 0.6, 0.7], 1, 0.25),
            call([0.5, 0.48, 0.3, 0.6, 0.7], 2, 0.25),
        ]
    )


@patch(
    "modules.cutting.dodecagon.are_parallel_lines",
    side_effect=[True, True, True, True],
)
def test_is_line_parallel_to_all_lines_when_parallel(mock_are_parallel_lines):
    assert is_line_parallel_to_all_lines(
        [0.02, 0.3, 0.05, 0.048, 0.03, 0.06, 0.07], 2, 0.25
    )
    assert mock_are_parallel_lines.call_count == 4
    mock_are_parallel_lines.assert_has_calls(
        [
            call(0.05, 0.048, 0.25),
            call(0.05, 0.03, 0.25),
            call(0.05, 0.06, 0.25),
            call(0.05, 0.07, 0.25),
        ]
    )


@patch(
    "modules.cutting.dodecagon.are_parallel_lines",
    side_effect=[True, False, False, True, True],
)
def test_is_line_parallel_to_all_lines_when_not_parallel(mock_are_parallel_lines):
    assert not is_line_parallel_to_all_lines(
        [0.02, 0.3, 0.05, 0.048, 0.03, 0.06, 0.07], 1, 0.25
    )
    assert mock_are_parallel_lines.call_count == 2
    mock_are_parallel_lines.assert_has_calls(
        [
            call(0.3, 0.05, 0.25),
            call(0.3, 0.048, 0.25),
        ]
    )
