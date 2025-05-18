from PIL import Image
import numpy as np
from unittest.mock import patch, call, Mock

from modules.smearing.check_smeared_image import (
    compare_decay,
    general_decay,
    spectrogram_FFT,
    vertical_decay,
    block_decay,
)


@patch("modules.smearing.check_smeared_image.np.ndarray", 5)
@patch("modules.smearing.check_smeared_image.general_decay")
@patch("modules.smearing.check_smeared_image.block_decay")
@patch("modules.smearing.check_smeared_image.isinstance", return_value=True)
@patch("modules.smearing.check_smeared_image.np.abs", return_value="return from abs")
@patch("modules.smearing.check_smeared_image.np.mean", return_value="return from mean")
def test_compare_decay(
    mock_mean, mock_abs, mock_isinstance, mock_block_decay, mock_general_decay
):
    general_decay_result = np.array([10, 29, 30, 40, 50])
    block_decay_result = np.array([1, 2, 3, 4, 5])
    mock_general_decay.return_value = general_decay_result
    mock_block_decay.return_value = block_decay_result
    image_array_example = np.array(
        [
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
        ]
    )
    assert compare_decay(image_array_example) == "return from mean"
    mock_general_decay.assert_called_once_with(image_array_example)
    mock_block_decay.assert_called_once_with(image_array_example, general_decay_result)
    mock_isinstance.assert_called_once_with(block_decay_result, 5)
    np.testing.assert_array_equal(
        mock_abs.call_args[0][0], np.array([9, 27, 27, 36, 45])
    )
    mock_mean.assert_called_once_with("return from abs")


@patch("modules.smearing.check_smeared_image.np.ndarray", 5)
@patch("modules.smearing.check_smeared_image.general_decay")
@patch("modules.smearing.check_smeared_image.block_decay", return_value="not ndarray")
@patch("modules.smearing.check_smeared_image.isinstance", return_value=False)
@patch("modules.smearing.check_smeared_image.np.abs", return_value="return from abs")
@patch("modules.smearing.check_smeared_image.np.mean", return_value="return from mean")
def test_compare_decay_when_isinstance_return_false(
    mock_mean, mock_abs, mock_isinstance, mock_block_decay, mock_general_decay
):
    general_decay_result = np.array([10, 29, 30, 40, 50])
    mock_general_decay.return_value = general_decay_result
    image_array_example = np.array(
        [
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
        ]
    )
    assert not compare_decay(image_array_example)
    mock_general_decay.assert_called_once_with(image_array_example)
    mock_block_decay.assert_called_once_with(image_array_example, general_decay_result)
    mock_isinstance.assert_called_once_with("not ndarray", 5)
    mock_abs.assert_not_called()
    mock_mean.assert_not_called()


@patch(
    "modules.smearing.check_smeared_image.spectrogram_FFT",
    return_value="spectrogram_FFT",
)
@patch("modules.smearing.check_smeared_image.vertical_decay")
def test_general_decay(mock_vertical_decay, mock_spectrogram_FFT):
    image = Mock(Image.fromarray(np.zeros((100, 153, 3), dtype=np.uint8)))
    general_decay(image)
    mock_spectrogram_FFT.assert_called_once_with(image)
    mock_vertical_decay.assert_called_once_with("spectrogram_FFT")


@patch(
    "modules.smearing.check_smeared_image.np.fft.fft2", return_value="return from fft2"
)
@patch(
    "modules.smearing.check_smeared_image.np.fft.fftshift",
    return_value="return from fftshift",
)
@patch("modules.smearing.check_smeared_image.np.abs")
def test_spectrogram_FFT(mock_abs, mock_fftshift, mock_fft2):
    image = Mock(Image.fromarray(np.zeros((100, 153, 3), dtype=np.uint8)))
    spectrogram_FFT(image)
    mock_fft2.assert_called_once_with(image)
    mock_fftshift.assert_called_once_with("return from fft2")
    mock_abs.assert_called_once_with("return from fftshift")


@patch(
    "modules.smearing.check_smeared_image.np.fft.fftfreq",
    side_effect=[
        np.array([0.0, 0.5]),
        np.array([0.0, 0.16666667, 0.33333333, -0.5, -0.33333333, -0.16666667]),
    ],
)
def test_vertical_decay(mock_fftfreq):
    spectrogram = np.array([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]])
    result = vertical_decay(spectrogram)
    mock_fftfreq.assert_has_calls(
        [
            call(2),
            call(6),
        ]
    )
    assert mock_fftfreq.call_count == 2

    assert isinstance(result, np.ndarray)


@patch("modules.smearing.check_smeared_image.COORDINATES_OF_BLOCK", (0, 0))
@patch("modules.smearing.check_smeared_image.BLOCK_SIZE", (1, 1))
@patch(
    "modules.smearing.check_smeared_image.spectrogram_FFT",
    return_value=np.array([[454, 13, 45], [677, 123, 45]]),
)
@patch(
    "modules.smearing.check_smeared_image.cv2.resize",
    return_value="resized_spectrogram",
)
@patch("modules.smearing.check_smeared_image.vertical_decay")
def test_block_decay(mock_vertical_decay, mock_resize, mock_spectrogram_FFT):
    image = Image.fromarray(np.zeros((100, 153, 3), dtype=np.uint8))
    spectrogram = np.array([[12, 13, 45], [456, 123, 45]])
    block_decay(np.array(image), spectrogram)
    mock_spectrogram_FFT.assert_called_once()
    np.testing.assert_array_equal(
        np.array([[454, 13, 45], [677, 123, 45]]), mock_resize.call_args[0][0]
    )
    assert mock_resize.call_args[0][1] == spectrogram.shape[::-1]
    mock_vertical_decay.assert_called_once_with("resized_spectrogram")


@patch("modules.smearing.check_smeared_image.COORDINATES_OF_BLOCK", (100, 100))
@patch("modules.smearing.check_smeared_image.BLOCK_SIZE", (50, 50))
@patch(
    "modules.smearing.check_smeared_image.spectrogram_FFT",
    return_value=np.array([[454, 13, 45], [677, 123, 45]]),
)
@patch(
    "modules.smearing.check_smeared_image.cv2.resize",
    return_value="resized_spectrogram",
)
@patch("modules.smearing.check_smeared_image.vertical_decay")
def test_block_decay_with_small_sub_image(
    mock_vertical_decay, mock_resize, mock_spectrogram_FFT
):
    image = Image.fromarray(np.zeros((100, 153, 3), dtype=np.uint8))
    spectrogram = np.array([[12, 13, 45], [456, 123, 45]])
    block_decay(np.array(image), spectrogram)
    mock_spectrogram_FFT.assert_not_called()
    mock_resize.assert_not_called()
    mock_vertical_decay.assert_not_called()
