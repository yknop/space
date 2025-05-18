from unittest.mock import patch
import numpy as np

from modules.smearing.check_smooth import (
    is_smooth_region,
    gradient_energy,
    variance_of_laplacian,
    gaussian_blur_difference,
)


class MockImage:
    def astype(self, flag):
        return np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
            ]
        )

    def var(self):
        return 20


@patch("modules.smearing.check_smooth.gradient_energy", return_value=350)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=40)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.7)
def test_detect_smooth_by_sobel(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_not_called()
    mock_gaussian_blur_difference.assert_not_called()


@patch("modules.smearing.check_smooth.gradient_energy", return_value=900)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=40)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.7)
def test_detect_no_smooth_by_sobel(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert not is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_not_called()
    mock_gaussian_blur_difference.assert_not_called()


@patch("modules.smearing.check_smooth.gradient_energy", return_value=500)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=40)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.6)
def test_detect_smooth_by_laplacian_and_gaussian(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_called_once_with("image")
    mock_gaussian_blur_difference.assert_called_once_with("image")


@patch("modules.smearing.check_smooth.gradient_energy", return_value=500)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=60)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.8)
def test_detect_no_smooth_by_laplacian_and_gaussian(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert not is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_called_once_with("image")
    mock_gaussian_blur_difference.assert_called_once_with("image")


@patch("modules.smearing.check_smooth.gradient_energy", return_value=500)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=60)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.6)
def test_detect_smooth_by_gaussian(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_called_once_with("image")
    mock_gaussian_blur_difference.assert_called_once_with("image")


@patch("modules.smearing.check_smooth.gradient_energy", return_value=500)
@patch("modules.smearing.check_smooth.variance_of_laplacian", return_value=40)
@patch("modules.smearing.check_smooth.gaussian_blur_difference", return_value=1.8)
def test_detect_no_smooth_by_gaussian(
    mock_gaussian_blur_difference, mock_variance_of_laplacian, mock_gradient_energy
):
    assert not is_smooth_region(
        "image", {"sobel_value": 400, "laplacian_value": 50, "blur_value": 1.7}
    )
    mock_gradient_energy.assert_called_once_with("image")
    mock_variance_of_laplacian.assert_called_once_with("image")
    mock_gaussian_blur_difference.assert_called_once_with("image")


@patch("modules.smearing.check_smooth.cv2.Sobel")
@patch("modules.smearing.check_smooth.np.abs")
@patch("modules.smearing.check_smooth.np.mean")
def test_gradient_energy(mock_mean, mock_abs, mock_sobel):
    mock_sobel.side_effect = [
        np.array(
            [
                [-1.0, 2.0, 3.0],
                [4.0, -5.0, 6.0],
                [7.0, 8.0, -9.0],
            ]
        ),
        np.array(
            [
                [1.0, -2.0, 3.0],
                [-4.0, 5.0, 6.0],
                [7.0, -8.0, 9.0],
            ]
        ),
    ]
    mock_abs.side_effect = [
        np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
            ]
        ),
        np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
            ]
        ),
    ]
    mock_mean.side_effect = [5.0, 5.0]
    assert gradient_energy("image") == 10.0


@patch("modules.smearing.check_smooth.cv2.Laplacian")
def test_variance_of_laplacian(mock_laplacian):
    mock_image = MockImage()
    mock_laplacian.return_value = mock_image
    assert variance_of_laplacian(mock_image) == 20


@patch("modules.smearing.check_smooth.np.float32", 3)
@patch("modules.smearing.check_smooth.cv2.GaussianBlur")
@patch("modules.smearing.check_smooth.np.abs", return_value="return from np.abs.")
@patch("modules.smearing.check_smooth.np.mean", return_value="return from np.mean.")
def test_gaussian_blur_difference(mock_mean, mock_abs, mock_gaussian_blur):
    mock_image = MockImage()
    mock_blurred = MockImage()
    mock_gaussian_blur.return_value = mock_blurred
    assert gaussian_blur_difference(mock_image) == "return from np.mean."
    mock_gaussian_blur.assert_called_once_with(mock_image, (5, 5), 0)
    np.testing.assert_array_equal(
        np.array(
            [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        ),
        mock_abs.call_args[0][0],
    )
    mock_mean.assert_called_once_with("return from np.abs.")
