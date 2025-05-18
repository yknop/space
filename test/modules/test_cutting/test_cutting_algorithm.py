from enum import Enum
from unittest.mock import patch, call
import pytest

from modules.cutting.cutting_algorithm import (
    cutting_disruption,
    is_cut,
    is_not_polygon,
)


class Disruptions(Enum):
    CUT_IMAGE = "cut_image"


@patch("modules.cutting.cutting_algorithm.Disruptions", Disruptions)
@patch(
    "modules.cutting.cutting_algorithm.get_consts_cutting_image", return_value="consts"
)
@patch("modules.cutting.cutting_algorithm.is_cut", return_value=True)
@patch("modules.cutting.cutting_algorithm.add_disruption")
def test_cutting_disruption_when_is_cut_return_True(
    mock_add_disruption, mock_is_cut, mock_get_consts_cutting_image
):
    cutting_disruption(
        "db",
        "image_path",
        "image_id",
        "example_satellite_name",
        "json_file_path",
        "shape",
        background_image="background_image",
    )
    mock_get_consts_cutting_image.assert_called_once_with("example_satellite_name")
    mock_is_cut.assert_called_once_with(
        "background_image", "json_file_path", "shape", "consts"
    )
    mock_add_disruption.assert_called_once_with("db", "image_id", "cut_image")


@patch("modules.cutting.cutting_algorithm.Disruptions", Disruptions)
@patch(
    "modules.cutting.cutting_algorithm.get_consts_cutting_image", return_value="consts"
)
@patch("modules.cutting.cutting_algorithm.is_cut", return_value=False)
@patch("modules.cutting.cutting_algorithm.add_disruption")
def test_cutting_disruption_when_is_cut_return_False(
    mock_add_disruption, mock_is_cut, mock_get_consts_cutting_image
):
    cutting_disruption(
        "db",
        "image_path",
        "image_id",
        "example_satellite_name",
        "json_file_path",
        "shape",
        background_image="background_image",
    )
    mock_get_consts_cutting_image.assert_called_once_with("example_satellite_name")
    mock_is_cut.assert_called_once_with(
        "background_image", "json_file_path", "shape", "consts"
    )
    mock_add_disruption.assert_not_called()


@patch("modules.cutting.cutting_algorithm.is_not_polygon", return_value=True)
@patch("modules.cutting.cutting_algorithm.get_vertices", return_value="vertices")
@patch("modules.cutting.cutting_algorithm.is_parallelogram", return_value=False)
@patch("modules.cutting.cutting_algorithm.is_dodecagon", return_value=False)
def test_is_cut_when_is_not_polygon(
    mock_is_dodecagon, mock_is_parallelogram, mock_get_vertices, mock_is_not_polygon
):
    assert is_cut(
        "background_image",
        "json_file_path",
        "parallelogram",
        {
            "epsilon_coefficient": 0.01,
            "min_contour_area": 50000,
            "slope_difference_threshold_value": 0.25,
        },
    )
    mock_is_not_polygon.assert_called_once_with("json_file_path")
    mock_get_vertices.assert_not_called()
    mock_is_parallelogram.assert_not_called()
    mock_is_dodecagon.assert_not_called()


@patch("modules.cutting.cutting_algorithm.is_not_polygon", return_value=False)
@patch("modules.cutting.cutting_algorithm.get_vertices", return_value="vertices")
@patch("modules.cutting.cutting_algorithm.is_parallelogram", side_effect=[True, False])
@patch("modules.cutting.cutting_algorithm.is_dodecagon", return_value=False)
def test_is_cut_when_shape_parallelogram(
    mock_is_dodecagon, mock_is_parallelogram, mock_get_vertices, mock_is_not_polygon
):
    assert not is_cut(
        "background_image",
        "json_file_path",
        "parallelogram",
        {
            "epsilon_coefficient": 0.01,
            "min_contour_area": 50000,
            "slope_difference_threshold_value": 0.25,
        },
    )
    assert is_cut(
        "background_image",
        "json_file_path",
        "parallelogram",
        {
            "epsilon_coefficient": 0.01,
            "min_contour_area": 50000,
            "slope_difference_threshold_value": 0.25,
        },
    )
    assert mock_is_not_polygon.call_count == 2
    mock_is_not_polygon.assert_has_calls(
        [
            call("json_file_path"),
            call("json_file_path"),
        ]
    )
    assert mock_get_vertices.call_count == 2
    mock_get_vertices.assert_has_calls(
        [
            call("background_image", 0.01),
            call("background_image", 0.01),
        ]
    )
    assert mock_is_parallelogram.call_count == 2
    mock_is_parallelogram.assert_has_calls(
        [
            call("vertices", 0.25),
            call("vertices", 0.25),
        ]
    )
    mock_is_dodecagon.assert_not_called()


@patch("modules.cutting.cutting_algorithm.is_not_polygon", return_value=False)
@patch("modules.cutting.cutting_algorithm.get_vertices", return_value="vertices")
@patch("modules.cutting.cutting_algorithm.is_parallelogram", return_value=False)
@patch("modules.cutting.cutting_algorithm.is_dodecagon", side_effect=[True, False])
def test_is_cut_when_shape_dodecagon(
    mock_is_dodecagon,
    mock_is_parallelogram,
    mock_get_vertices,
    mock_is_not_polygon,
):
    assert not is_cut(
        "background_image",
        "json_file_path",
        "dodecagon",
        {
            "epsilon_coefficient": 0.01,
            "min_contour_area": 50000,
            "slope_difference_threshold_value": 0.25,
        },
    )
    assert is_cut(
        "background_image",
        "json_file_path",
        "dodecagon",
        {
            "epsilon_coefficient": 0.01,
            "min_contour_area": 50000,
            "slope_difference_threshold_value": 0.25,
        },
    )
    assert mock_is_not_polygon.call_count == 2
    mock_is_not_polygon.assert_has_calls(
        [
            call("json_file_path"),
            call("json_file_path"),
        ]
    )
    assert mock_get_vertices.call_count == 2
    mock_get_vertices.assert_has_calls(
        [
            call("background_image", 0.01),
            call("background_image", 0.01),
        ]
    )
    mock_is_parallelogram.assert_not_called()
    assert mock_is_dodecagon.call_count == 2
    mock_is_dodecagon.assert_has_calls(
        [
            call("vertices", 0.25),
            call("vertices", 0.25),
        ]
    )


@patch("modules.cutting.cutting_algorithm.is_not_polygon", return_value=False)
@patch("modules.cutting.cutting_algorithm.get_vertices", return_value="vertices")
@patch("modules.cutting.cutting_algorithm.is_parallelogram", return_value=False)
@patch("modules.cutting.cutting_algorithm.is_dodecagon", return_value=False)
def test_is_cut_assert_raise_exception_when_shape_is_not_supported(
    mock_is_dodecagon, mock_is_parallelogram, mock_get_vertices, mock_is_not_polygon
):
    with pytest.raises(ValueError, match="The shape: triangle is not supported."):
        is_cut(
            "background_image",
            "json_file_path",
            "triangle",
            {
                "epsilon_coefficient": 0.01,
                "min_contour_area": 50000,
                "slope_difference_threshold_value": 0.25,
            },
        )
    mock_is_not_polygon.assert_called_once_with("json_file_path")
    mock_get_vertices.assert_called_once_with("background_image", 0.01)
    mock_is_parallelogram.assert_not_called()
    mock_is_dodecagon.assert_not_called()


@patch(
    "modules.cutting.cutting_algorithm.get_value_by_keys",
    side_effect=["Polygon", "MultiPolygon"],
)
def test_is_not_polygon(mock_get_value_by_keys):
    assert not is_not_polygon("polygon_metadata.json")
    assert is_not_polygon("multipolygon_metadata.json")
    assert mock_get_value_by_keys.call_count == 2
    mock_get_value_by_keys.assert_has_calls(
        [
            call("polygon_metadata.json", ["geometry", "type"]),
            call("multipolygon_metadata.json", ["geometry", "type"]),
        ]
    )


@patch(
    "modules.cutting.cutting_algorithm.get_value_by_keys",
    side_effect=FileNotFoundError("File not found"),
)
def test_is_not_polygon_when_get_value_by_keys_raise_exception(mock_get_value_by_keys):
    with pytest.raises(
        Exception,
        match="When try read from metadata.json an error occured: File not found",
    ):
        is_not_polygon("metad.json")
    mock_get_value_by_keys.assert_called_once_with("metad.json", ["geometry", "type"])
