import numpy as np
import rasterio
from osgeo import gdal
from skimage import exposure
from typing import Tuple, Dict, Any

from utils.logger.write import logger


def convert_ntf_to_tif(input_image_ntf: str, output_image_tif: str) -> None:
    try:
        dataset = gdal.Open(input_image_ntf)
        gdal.Translate(output_image_tif, dataset, format="GTiff")
        dataset = None
        logger.info("NFT to TIFF conversion completed successfully")
    except Exception as error:
        error_log = "NFT to TIFF conversion failed"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def convert_image_to_8_bit(input_image: str, output_image: str) -> None:
    try:
        r, g, b, profile = get_8_bit_image_data(input_image)
        save_8_bit_image(output_image, r, g, b, profile)
    except Exception as error:
        raise Exception("Image to 8 bit conversion failed") from error


def get_8_bit_image_data(
    input_image: str,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    try:
        image = rasterio.open(input_image)
        profile = image.profile
        profile.update(dtype="uint8")
        r = normalize_to_uint8(image.read(1))
        g = normalize_to_uint8(image.read(2))
        b = normalize_to_uint8(image.read(3))
        image.close()
        return r, g, b, profile
    except Exception as error:
        raise Exception(
            "An error occurred while attempting to get 8-bit image data"
        ) from error


def normalize_to_uint8(array: np.ndarray) -> np.ndarray:
    background_value = 126
    background_mask = array == background_value
    array_scaled = array.copy()
    non_background_mask = ~background_mask
    rescaled_array = exposure.rescale_intensity(
        array[non_background_mask], in_range=(1, 4095), out_range=(0, 255)
    )
    array_scaled[non_background_mask] = np.ceil(rescaled_array).astype(np.uint8)
    array_scaled[background_mask] = 0
    return array_scaled


def save_8_bit_image(
    output_image: str,
    r: np.ndarray,
    g: np.ndarray,
    b: np.ndarray,
    profile: Dict[str, Any],
) -> None:
    try:
        image = rasterio.open(output_image, "w", **profile)
        image.write(r, 1)
        image.write(g, 2)
        image.write(b, 3)
        image.close()
    except Exception as error:
        raise Exception(
            "An error occurred while attempting to create an 8-bit tif image"
        ) from error
