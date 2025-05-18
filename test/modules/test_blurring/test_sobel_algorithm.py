import numpy as np
from unittest.mock import patch, call

from modules.blurring.sobel_algorithm import sobel_data


@patch("modules.blurring.sobel_algorithm.cv2.CV_64F", 0)
@patch("modules.blurring.sobel_algorithm.cv2.Sobel")
@patch("modules.blurring.sobel_algorithm.np.sqrt", return_value="sobel_result")
@patch("modules.blurring.sobel_algorithm.np.max", return_value=12)
@patch("modules.blurring.sobel_algorithm.np.mean", return_value=6.0)
@patch("modules.blurring.sobel_algorithm.np.var", return_value=18.0)
@patch(
    "modules.blurring.sobel_algorithm.decide_if_blur",
    return_value="return from decide_if_blur",
)
def test_sobel_data(
    mock_decide_if_blur,
    mock_var,
    mock_mean,
    mock_max,
    mock_sqrt,
    mock_sobel,
):
    mock_sobelx = np.array([1, 2])
    mock_sobely = np.array([2, 3])
    mock_sobel.side_effect = [mock_sobelx, mock_sobely]
    assert sobel_data("gray_image", [100, 200, 300]) == "return from decide_if_blur"
    mock_sobel.assert_has_calls(
        [call("gray_image", 0, 1, 0), call("gray_image", 0, 0, 1)]
    )
    np.testing.assert_array_equal(np.array([5, 13]), mock_sqrt.call_args[0][0])
    mock_max.assert_called_once_with("sobel_result")
    mock_mean.assert_called_once_with("sobel_result")
    mock_var.assert_called_once_with("sobel_result")
    mock_decide_if_blur.assert_called_once_with(12, 6, 18, [100, 200, 300])
