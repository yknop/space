from typing import Any, Dict

from consts.blur import (
    BLACKSKY_BLUR_PERCENTAGE_THRESHOLD_VALUE,
    BLACKSKY_LAPLACIAN_THRESHOLD_VALUES,
    BLACKSKY_ROBERT_THRESHOLD_VALUES,
    BLACKSKY_SOBEL_THRESHOLD_VALUES,
)
from consts.cutting import (
    BLACKSKY_EPSILON_COEFFICIENT,
    SLOPE_DIFFERENCE_THRESHOLD_VALUE,
)
from consts.manage_images import BLACKSKY_SUB_IMAGE_SIZE
from consts.satellites import SATELLITES
from consts.saturation import (
    BLACKSKY_GRID_SIZE,
    BLACKSKY_SATURATION_DISRUPTION_PERCENT,
    BLACKSKY_SATURATION_SQUARE_PERCENT,
    BLACKSKY_SATURATION_THRESHOLD_VALUE,
)
from consts.smear import (
    BLACKSKY_BLUR_THRESHOLD_VALUE,
    BLACKSKY_LAPLACIAN_THRESHOLD_VALUE,
    BLACKSKY_SMEAR_PERCENTAGE_THRESHOLD_VALUE,
    BLACKSKY_SMEAR_THRESHOLD_VALUE,
    BLACKSKY_SOBEL_THRESHOLD_VALUE,
)
from utils.logger.write import get_logger


def get_consts_blur(satellite_name: str) -> Dict[str, Any]:
    match satellite_name:
        case "BlackSky":
            return {
                "sub_image_size": BLACKSKY_SUB_IMAGE_SIZE,
                "percentage_threshold_value": BLACKSKY_BLUR_PERCENTAGE_THRESHOLD_VALUE,
                "laplacian_threshold_values": BLACKSKY_LAPLACIAN_THRESHOLD_VALUES,
                "robert_threshold_values": BLACKSKY_ROBERT_THRESHOLD_VALUES,
                "sobel_threshold_values": BLACKSKY_SOBEL_THRESHOLD_VALUES,
            }
        case _:
            raise Exception("Unsupported satellite.")


def get_consts_saturation(satellite_name: str) -> Dict[str, Any]:
    match satellite_name:
        case "BlackSky":
            return {
                "grid_size": BLACKSKY_GRID_SIZE,
                "disruption_percent": BLACKSKY_SATURATION_DISRUPTION_PERCENT,
                "square_percent": BLACKSKY_SATURATION_SQUARE_PERCENT,
                "threshold_value": BLACKSKY_SATURATION_THRESHOLD_VALUE,
            }
        case _:
            raise Exception("Unsupported satellite.")


def get_consts_smear(satellite_name: str) -> Dict[str, Any]:
    match satellite_name:
        case "BlackSky":
            return {
                "size": BLACKSKY_SUB_IMAGE_SIZE,
                "percentage_threshold_value": BLACKSKY_SMEAR_PERCENTAGE_THRESHOLD_VALUE,
                "threshold_value": BLACKSKY_SMEAR_THRESHOLD_VALUE,
                "sobel_value": BLACKSKY_SOBEL_THRESHOLD_VALUE,
                "laplacian_value": BLACKSKY_LAPLACIAN_THRESHOLD_VALUE,
                "blur_value": BLACKSKY_BLUR_THRESHOLD_VALUE,
            }
        case _:
            raise Exception("Unsupported satellite.")


def get_consts_cutting_image(satellite_name: str) -> Dict[str, Any]:
    match satellite_name:
        case "BlackSky":
            return {
                "epsilon_coefficient": BLACKSKY_EPSILON_COEFFICIENT,
                "slope_difference_threshold_value": SLOPE_DIFFERENCE_THRESHOLD_VALUE,
            }
        case _:
            raise Exception("Unsupported satellite.")


def get_satellite_details(company: str) -> Dict[str, Any]:
    try:
        return SATELLITES[company]
    except KeyError as error:
        error_log = "No document found for company '{company}'"
        get_logger().error(error_log, exc_info=True)
        raise ValueError(error_log) from error
