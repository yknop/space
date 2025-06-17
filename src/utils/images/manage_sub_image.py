import numpy as np
import rasterio
from rasterio.windows import Window

from utils.logger.write import get_logger

logger = get_logger()


def extract_sub_image_array(
    img_path: str, x: int, y: int, width_size: int, height_size: int
) -> np.uint8:
    try:
        with rasterio.open(img_path) as src_image:
            window = Window(x, y, width_size, height_size)
            sub_image = src_image.read([1, 2, 3], window=window)
            sub_image = np.transpose(sub_image, (1, 2, 0))
        return sub_image
    except Exception as error:
        error_log = "An error occurred when extracting sub-image array"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
