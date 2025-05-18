from unittest.mock import patch
import pytest
import numpy as np

from modules.cutting.vertices import (
    get_vertices,
    get_vertices_from_contours,
)


def mock_contour_area(vertex):
    return vertex[0]


class MockNumpyArray:
    def astype(self, type):
        return "thresholded"


@patch("modules.cutting.vertices.cv2.RETR_TREE", 2)
@patch("modules.cutting.vertices.cv2.CHAIN_APPROX_SIMPLE", 3)
@patch("modules.cutting.vertices.np.where", return_value=MockNumpyArray())
@patch("modules.cutting.vertices.cv2.findContours", return_value=([[1, 3]], ""))
@patch(
    "modules.cutting.vertices.get_vertices_from_contours",
    return_value=[[0, 0], [0, 20], [20, 20], [20, 0]],
)
def test_get_vertices(
    mock_get_vertices_from_contours,
    mock_find_contours,
    mock_np_where,
):
    background_image = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    assert get_vertices(
        background_image,
        0.01,
    ) == [[0, 0], [0, 20], [20, 20], [20, 0]]
    assert len(mock_np_where.call_args[0]) == 3
    np.testing.assert_array_equal(
        mock_np_where.call_args[0][0],
        np.array(
            [
                [True, True, True, True, True],
                [True, False, False, False, True],
                [True, True, False, False, True],
                [True, False, False, False, True],
                [True, True, True, True, True],
            ]
        ),
    )
    assert mock_np_where.call_args[0][1] == 0
    assert mock_np_where.call_args[0][2] == 255
    mock_find_contours.assert_called_once_with("thresholded", 2, 3)
    mock_get_vertices_from_contours.assert_called_once_with(
        [[1, 3]],
        0.01,
    )


@patch("modules.cutting.vertices.cv2.RETR_TREE", 2)
@patch("modules.cutting.vertices.cv2.CHAIN_APPROX_SIMPLE", 3)
@patch("modules.cutting.vertices.np.where", return_value=MockNumpyArray())
@patch("modules.cutting.vertices.cv2.findContours", return_value=(None, ""))
@patch(
    "modules.cutting.vertices.get_vertices_from_contours",
    return_value=[[0, 0], [0, 20], [20, 20], [20, 0]],
)
def test_get_vertices_when_return_none_for_contours(
    mock_get_vertices_from_contours,
    mock_find_contours,
    mock_np_where,
):
    background_image = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    with pytest.raises(Exception, match="No contours found."):
        get_vertices(
            background_image,
            0.01,
        )
    assert len(mock_np_where.call_args[0]) == 3
    np.testing.assert_array_equal(
        mock_np_where.call_args[0][0],
        np.array(
            [
                [True, True, True, True, True],
                [True, False, False, False, True],
                [True, True, False, False, True],
                [True, False, False, False, True],
                [True, True, True, True, True],
            ]
        ),
    )
    assert mock_np_where.call_args[0][1] == 0
    assert mock_np_where.call_args[0][2] == 255
    mock_find_contours.assert_called_once_with("thresholded", 2, 3)
    mock_get_vertices_from_contours.assert_not_called()


@patch("modules.cutting.vertices.cv2.contourArea", mock_contour_area)
@patch("modules.cutting.vertices.cv2.arcLength", return_value=60)
@patch(
    "modules.cutting.vertices.cv2.approxPolyDP",
    return_value=[[[0, 10]], [[10, 10]], [[10, 0]], [[0, 0]]],
)
def test_get_vertices_from_contours(mock_approx_poly_dp, mock_arc_length):
    assert get_vertices_from_contours([[5], [6], [0], [3], [10], [5]], 0.01) == [
        [0, 10],
        [10, 10],
        [10, 0],
        [0, 0],
    ]
    mock_arc_length.assert_called_once_with([10], True)
    mock_approx_poly_dp.assert_called_once_with([10], 0.6, True)
