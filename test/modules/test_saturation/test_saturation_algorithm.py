import numpy as np
from unittest.mock import patch
from enum import Enum

from modules.saturation.saturation_algorithm import (
    saturation_disruption,
    saturation_check,
    saturation_check_use_grid,
    calculate_saturation,
    saturated_square,
    is_saturation_image,
    percent,
)


class Disruptions(Enum):
    SATURATION = "saturation"


def mock_image():
    return np.zeros((100, 100, 3), dtype=np.uint8)


@patch("modules.saturation.saturation_algorithm.Disruptions", Disruptions)
@patch("modules.saturation.saturation_algorithm.add_disruption")
@patch(
    "modules.saturation.saturation_algorithm.create_polygon",
    return_value=["polygons"],
)
@patch(
    "modules.saturation.saturation_algorithm.saturation_check",
    return_value=[True, ["points"]],
)
@patch("modules.saturation.saturation_algorithm.cv2.imread", return_value="image")
def test_saturation_disruption(
    mock_imread,
    mock_saturation_check,
    mock_create_polygon,
    mock_add_disruption,
):
    image_path = "test/mock_img.png"
    saturation_disruption("db", image_path, 5, "example_satellite_name")
    mock_imread.assert_called_once_with("test/mock_img.png")
    mock_saturation_check.assert_called_once_with("image", "example_satellite_name")
    mock_create_polygon.assert_called_once_with(["points"])
    mock_add_disruption.assert_called_once_with("db", 5, "saturation", ["polygons"])


@patch("modules.saturation.saturation_algorithm.is_saturation_image", return_value=True)
@patch(
    "modules.saturation.saturation_algorithm.saturation_check_use_grid",
    return_value=[100, []],
)
@patch("modules.saturation.saturation_algorithm.get_consts_saturation")
def test_saturation_check(
    mock_get_consts_saturation, mock_saturated_pixels_use_grid, mock_percent
):
    image = mock_image()
    saturated_image, saturated_squares = saturation_check(
        image, "example_satellite_name"
    )
    assert saturated_image
    assert type(saturated_squares) is list
    mock_get_consts_saturation.assert_called_once_with("example_satellite_name")


@patch("modules.saturation.saturation_algorithm.saturated_square", return_value=100)
def test_saturation_check_use_grid(mock_saturated_square):
    image = mock_image()
    sum_saturated_pixels, saturated_squares = saturation_check_use_grid(
        image,
        {
            "grid_size": 50,
            "disruption_percent": 100,
            "square_percent": 250,
            "threshold_value": [2550, 2550, 2550],
        },
    )
    assert mock_saturated_square.call_count == 4
    assert sum_saturated_pixels == 100 * 4
    assert type(saturated_squares) is list


@patch("modules.saturation.saturation_algorithm.calculate_saturation", return_value=300)
@patch("modules.saturation.saturation_algorithm.percent", return_value=30)
def test_saturated_square(mock_percent, mock_calculate_saturation):
    image = mock_image()
    saturated_squares = []
    saturated_pixels = saturated_square(
        image,
        1,
        1,
        saturated_squares,
        {
            "grid_size": 50,
            "disruption_percent": 100,
            "square_percent": 25,
            "threshold_value": [2550, 2550, 2550],
        },
    )
    assert saturated_pixels == 300
    assert saturated_squares == [[(1, 1), (51, 51)]]


def test_all_pixels_white():
    square = np.full((10, 10, 3), [255, 255, 255], dtype=np.uint8)
    assert calculate_saturation(square, 241) == 100


def test_no_pixels_white():
    square = np.zeros((10, 10, 3), dtype=np.uint8)
    assert calculate_saturation(square, 241) == 0


def test_some_pixels_white():
    square = np.zeros((10, 10, 3), dtype=np.uint8)
    square[3, 3] = [255, 255, 255]
    square[5, 5] = [255, 255, 255]
    assert calculate_saturation(square, 241) == 2


def test_is_saturation_image():
    image = mock_image()
    saturation_image = is_saturation_image(image, 5000, 25)
    assert saturation_image


def test_percent():
    assert percent(100, 400) == 25
    assert percent(5, 0) == 0
