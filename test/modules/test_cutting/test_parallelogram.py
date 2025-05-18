from unittest.mock import patch, call

from modules.cutting.parallelogram import is_parallelogram


@patch("modules.cutting.parallelogram.get_slope", side_effect=[1, 1, -1, -1])
@patch("modules.cutting.parallelogram.are_parallel_lines", side_effect=[True, True])
def test_is_parallelogram_when_is_parallelogram(
    mock_are_parallel_lines, mock_get_slope
):
    assert is_parallelogram([[0, 0], [5, 5], [10, 0], [5, -5]], 0.25)
    assert mock_get_slope.call_count == 4
    mock_get_slope.assert_has_calls(
        [
            call([0, 0], [5, 5]),
            call([10, 0], [5, -5]),
            call([5, 5], [10, 0]),
            call([5, -5], [0, 0]),
        ]
    )
    assert mock_are_parallel_lines.call_count == 2
    mock_are_parallel_lines.assert_has_calls(
        [
            call(1, 1, 0.25),
            call(-1, -1, 0.25),
        ]
    )


@patch("modules.cutting.parallelogram.get_slope", side_effect=[1, 1, -1, -1])
@patch("modules.cutting.parallelogram.are_parallel_lines", side_effect=[True, True])
def test_is_parallelogram_when_num_vertices_not_4(
    mock_are_parallel_lines, mock_get_slope
):
    assert not is_parallelogram([[0, 0], [5, 5], [10, 0]], 0.25)
    mock_get_slope.assert_not_called()
    mock_are_parallel_lines.assert_not_called()


@patch("modules.cutting.parallelogram.get_slope", side_effect=[1, 0.2, -1, -0.2])
@patch("modules.cutting.parallelogram.are_parallel_lines", side_effect=[False, True])
def test_is_parallelogram_when_is_not_parallel(mock_are_parallel_lines, mock_get_slope):
    assert not is_parallelogram([[0, 0], [5, 5], [10, 0], [5, -1]], 0.25)
    assert mock_get_slope.call_count == 2
    mock_get_slope.assert_has_calls([call([0, 0], [5, 5]), call([10, 0], [5, -1])])
    mock_are_parallel_lines.assert_called_once_with(1, 0.2, 0.25)
