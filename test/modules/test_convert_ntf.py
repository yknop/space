from unittest.mock import patch, call
import numpy as np
import pytest

from utils.images.convert_ntf import (
    convert_ntf_to_tif,
    convert_image_to_8_bit,
    get_8_bit_image_data,
    normalize_to_uint8,
    save_8_bit_image,
)


class MockImage:
    def __init__(self, profile):
        self.profile = profile

    def read(self, num_band):
        return f"Band number {num_band}."

    def write(self, array, num_band):
        return

    def close(self):
        return


@patch("modules.convert_ntf.gdal.Open", return_value="gdal_open_dataset")
@patch("modules.convert_ntf.gdal.Translate")
def test_convert_ntf_to_tif(mock_gdal_translate, mock_gdal_open):
    convert_ntf_to_tif("input_image_ntf.ntf", "output_image_tif.tif")
    mock_gdal_open.assert_called_once_with("input_image_ntf.ntf")
    mock_gdal_translate.assert_called_once_with(
        "output_image_tif.tif", "gdal_open_dataset", format="GTiff"
    )


@patch("modules.convert_ntf.gdal.Open", return_value="gdal_open_dataset")
@patch(
    "modules.convert_ntf.gdal.Translate",
    side_effect=Exception("Exception from gdal-translate."),
)
def test_convert_ntf_to_tif_when_gdal_translate_raise_exception(
    mock_gdal_translate, mock_gdal_open
):
    with pytest.raises(
        Exception,
        match="An error occurred while converting ntf to tif: Exception from gdal-translate.",
    ):
        convert_ntf_to_tif("input_image_ntf.ntf", "output_image_tif.tif")
    mock_gdal_open.assert_called_once_with("input_image_ntf.ntf")
    mock_gdal_translate.assert_called_once_with(
        "output_image_tif.tif", "gdal_open_dataset", format="GTiff"
    )


@patch(
    "modules.convert_ntf.get_8_bit_image_data", return_value=("r", "g", "b", "profile")
)
@patch("modules.convert_ntf.save_8_bit_image")
def test_convert_image_to_8_bit(mock_save_8_bit_image, mock_get_8_bit_image_data):
    convert_image_to_8_bit("input_image.tif", "output_image.tif")
    mock_get_8_bit_image_data.assert_called_once_with("input_image.tif")
    mock_save_8_bit_image.assert_called_once_with(
        "output_image.tif", "r", "g", "b", "profile"
    )


@patch(
    "modules.convert_ntf.rasterio.open",
    return_value=MockImage({"format": "GTiff", "dtype": "some_type"}),
)
@patch(
    "modules.convert_ntf.normalize_to_uint8",
    side_effect=[[1, 3, 4], [8, 3, 8], [3, 5, 3]],
)
def test_get_8_bit_image_data(mock_normalize_to_uint8, mock_rasterio_open):
    assert get_8_bit_image_data("input_image") == (
        [1, 3, 4],
        [8, 3, 8],
        [3, 5, 3],
        {"format": "GTiff", "dtype": "uint8"},
    )
    mock_rasterio_open.assert_called_once_with("input_image")
    assert mock_normalize_to_uint8.call_count == 3
    mock_normalize_to_uint8.assert_has_calls(
        [
            call("Band number 1."),
            call("Band number 2."),
            call("Band number 3."),
        ]
    )


@patch(
    "modules.convert_ntf.rasterio.open",
    side_effect=Exception("Exception from rasterio.open."),
)
@patch(
    "modules.convert_ntf.normalize_to_uint8",
    side_effect=[[1, 3, 4], [8, 3, 8], [3, 5, 3]],
)
def test_get_8_bit_image_data_when_rasterio_open_raise_exception(
    mock_normalize_to_uint8, mock_rasterio_open
):
    with pytest.raises(
        Exception,
        match="An error occurred while attempting to get 8-bit image data: Exception from rasterio.open.",
    ):
        get_8_bit_image_data("input_image")
    mock_rasterio_open.assert_called_once_with("input_image")
    mock_normalize_to_uint8.assert_not_called()


@patch(
    "modules.convert_ntf.exposure.rescale_intensity",
)
@patch(
    "modules.convert_ntf.np.ceil",
    return_value=np.array([54, 34.0, 65.0, 78, 154.0, 65, 29.0, 178, 29]),
)
def test_normalize_to_uint8(mock_ceil, mock_rescale_intensity):
    mock_rescale_intensity_return_value = np.array(
        [54, 33.5, 64.1, 78, 153.9, 65, 28.3, 178, 29]
    )
    mock_rescale_intensity.return_value = mock_rescale_intensity_return_value
    np.testing.assert_array_equal(
        normalize_to_uint8(
            np.array(
                [
                    [126, 126, 126, 126, 126],
                    [126, 1526, 1526, 1263, 126],
                    [126, 29, 1256, 29, 126],
                    [126, 29, 1256, 29, 126],
                    [126, 126, 126, 126, 126],
                ]
            )
        ),
        np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 54, 34, 65, 0],
                [0, 78, 154, 65, 0],
                [0, 29, 178, 29, 0],
                [0, 0, 0, 0, 0],
            ],
        ),
    )
    np.testing.assert_array_equal(
        np.array([1526, 1526, 1263, 29, 1256, 29, 29, 1256, 29]),
        mock_rescale_intensity.call_args[0][0],
    )
    mock_ceil.assert_called_once_with(mock_rescale_intensity_return_value)


@patch(
    "modules.convert_ntf.rasterio.open",
    return_value=MockImage({"format": "GTiff", "dtype": "uint8"}),
)
def test_save_8_bit_image(mock_rasterio_open):
    save_8_bit_image(
        "output_image.tif",
        [2, 4, 0],
        [3, 2, 4],
        [2, 4, 2],
        {"format": "GTiff", "dtype": "uint8"},
    )
    mock_rasterio_open.assert_called_once_with(
        "output_image.tif", "w", format="GTiff", dtype="uint8"
    )


@patch(
    "modules.convert_ntf.rasterio.open",
    side_effect=Exception("Exception from rasterio.open."),
)
def test_save_8_bit_image_when_rasterio_open_raise_exception(mock_rasterio_open):
    with pytest.raises(
        Exception,
        match="An error occurred while attempting to create an 8-bit tif image: Exception from rasterio.open.",
    ):
        save_8_bit_image(
            "output_image.tif",
            [2, 4, 0],
            [3, 2, 4],
            [2, 4, 2],
            {"format": "GTiff", "dtype": "uint8"},
        )
    mock_rasterio_open.assert_called_once_with(
        "output_image.tif", "w", format="GTiff", dtype="uint8"
    )
