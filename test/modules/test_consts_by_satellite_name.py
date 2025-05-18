import pytest
from unittest.mock import patch

from modules.consts_by_satellite_name import (
    get_consts_smear,
    get_consts_cutting_image,
    get_satellite_details,
)
from utils.consts.consts_by_satellite_name import get_consts_blur
from utils.consts.consts_by_satellite_name import get_consts_saturation


@patch("modules.consts_by_satellite_name.BLACKSKY_SUB_IMAGE_SIZE", 400)
@patch("modules.consts_by_satellite_name.BLACKSKY_BLUR_PERCENTAGE_THRESHOLD_VALUE", 10)
@patch(
    "modules.consts_by_satellite_name.BLACKSKY_LAPLACIAN_THRESHOLD_VALUES", [3, 5, 7]
)
@patch(
    "modules.consts_by_satellite_name.BLACKSKY_ROBERT_THRESHOLD_VALUES",
    [800, 900, 1000],
)
@patch(
    "modules.consts_by_satellite_name.BLACKSKY_SOBEL_THRESHOLD_VALUES", [100, 300, 500]
)
def test_get_consts_blur():
    assert get_consts_blur("BlackSky") == {
        "sub_image_size": 400,
        "percentage_threshold_value": 10,
        "laplacian_threshold_values": [3, 5, 7],
        "robert_threshold_values": [800, 900, 1000],
        "sobel_threshold_values": [100, 300, 500],
    }
    with pytest.raises(Exception, match="Unsupported satellite."):
        get_consts_blur("OtherSatellite")


@patch("modules.consts_by_satellite_name.BLACKSKY_GRID_SIZE", 7)
@patch("modules.consts_by_satellite_name.BLACKSKY_SATURATION_DISRUPTION_PERCENT", 10)
@patch("modules.consts_by_satellite_name.BLACKSKY_SATURATION_SQUARE_PERCENT", 25)
@patch(
    "modules.consts_by_satellite_name.BLACKSKY_SATURATION_THRESHOLD_VALUE",
    [255, 255, 255],
)
def test_get_consts_saturation():
    assert get_consts_saturation("BlackSky") == {
        "grid_size": 7,
        "disruption_percent": 10,
        "square_percent": 25,
        "threshold_value": [255, 255, 255],
    }
    with pytest.raises(Exception, match="Unsupported satellite."):
        get_consts_saturation("OtherSatellite")


@patch("modules.consts_by_satellite_name.BLACKSKY_SUB_IMAGE_SIZE", 400)
@patch("modules.consts_by_satellite_name.BLACKSKY_SMEAR_PERCENTAGE_THRESHOLD_VALUE", 10)
@patch("modules.consts_by_satellite_name.BLACKSKY_SMEAR_THRESHOLD_VALUE", 1200)
@patch("modules.consts_by_satellite_name.BLACKSKY_SOBEL_THRESHOLD_VALUE", 400)
@patch("modules.consts_by_satellite_name.BLACKSKY_LAPLACIAN_THRESHOLD_VALUE", 50)
@patch("modules.consts_by_satellite_name.BLACKSKY_BLUR_THRESHOLD_VALUE", 1.7)
def test_get_consts_smear():
    assert get_consts_smear("BlackSky") == {
        "size": 400,
        "percentage_threshold_value": 10,
        "threshold_value": 1200,
        "sobel_value": 400,
        "laplacian_value": 50,
        "blur_value": 1.7,
    }
    with pytest.raises(Exception, match="Unsupported satellite."):
        get_consts_smear("OtherSatellite")


@patch("modules.consts_by_satellite_name.BLACKSKY_EPSILON_COEFFICIENT", 0.001)
@patch("modules.consts_by_satellite_name.SLOPE_DIFFERENCE_THRESHOLD_VALUE", 0.25)
def test_get_consts_cutting_image():
    assert get_consts_cutting_image("BlackSky") == {
        "epsilon_coefficient": 0.001,
        "slope_difference_threshold_value": 0.25,
    }
    with pytest.raises(Exception, match="Unsupported satellite."):
        get_consts_cutting_image("OtherSatellite")


@patch(
    "modules.consts_by_satellite_name.SATELLITES",
    {
        "BlackSky": {"image_shape": "parallelogram"},
        "planet": {"image_shape": "dodecagon"},
    },
)
def test_get_satellite_details():
    assert get_satellite_details("BlackSky") == {"image_shape": "parallelogram"}


@patch(
    "modules.consts_by_satellite_name.SATELLITES",
    {
        "BlackSky": {"image_shape": "parallelogram"},
        "planet": {"image_shape": "dodecagon"},
    },
)
def test_get_satellite_details_error():
    with pytest.raises(ValueError, match="No document found for company 'airbus'"):
        get_satellite_details("airbus")
