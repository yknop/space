import numpy as np
import rasterio
from osgeo import gdal
from skimage import exposure

from utils.logger.write import get_logger

logger = get_logger()


def convert_ntf_to_tif(input_image_ntf: str, output_image_tif: str) -> None:
    try:
        dataset = gdal.Open(input_image_ntf)
        gdal.Translate(
            output_image_tif,
            dataset,
            format="GTiff",
            creationOptions=[
                "TILED=YES",
                "COMPRESS=NONE",
                "INTERLEAVE=BAND",
                "PREDICTOR=1",
            ],
        )
        dataset = None
        logger.info(f"NTF to TIFF: {input_image_ntf} → {output_image_tif}")
    except Exception as error:
        error_log = f"NTF to TIFF conversion failed for {input_image_ntf}"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def convert_image_to_8_bit(input_image: str, output_image: str) -> None:
    try:
        with rasterio.open(input_image) as image:
            profile = image.profile.copy()
            profile.update(dtype="uint8")

            r, g, b = image.read([1, 2, 3])
            r8 = normalize_to_uint8(r)
            g8 = normalize_to_uint8(g)
            b8 = normalize_to_uint8(b)

        with rasterio.open(output_image, "w", **profile) as image:
            image.write(r8, 1)
            image.write(g8, 2)
            image.write(b8, 3)

        logger.info(f"TIF to 8-bit: {input_image} → {output_image}")

    except Exception as error:
        raise Exception(f"8-bit conversion failed for {input_image}") from error


def normalize_to_uint8(array: np.ndarray) -> np.ndarray:
    background_value = 126
    background_mask = array == background_value

    if np.all(background_mask):
        return np.zeros_like(array, dtype=np.uint8)

    rescaled = exposure.rescale_intensity(
        array[~background_mask],
        in_range=(1, 4095),
        out_range=(0, 255),
    )

    output = np.zeros_like(array, dtype=np.uint8)
    output[~background_mask] = np.ceil(rescaled).astype(np.uint8)
    return output
