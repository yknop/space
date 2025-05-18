import numpy as np
from unittest.mock import patch, call, Mock

from modules.blurring.robert_algorithm import robert_data


@patch("modules.blurring.robert_algorithm.cv2.CV_64F", 0)
@patch("modules.blurring.robert_algorithm.np.array")
@patch("modules.blurring.robert_algorithm.cv2.filter2D")
@patch("modules.blurring.robert_algorithm.np.sqrt", Mock(return_value="robert_result"))
@patch("modules.blurring.robert_algorithm.np.max", return_value=12)
@patch("modules.blurring.robert_algorithm.np.mean", return_value=6.0)
@patch("modules.blurring.robert_algorithm.np.var", return_value=18.0)
@patch(
    "modules.blurring.robert_algorithm.decide_if_blur",
    return_value="return from decide_if_blur",
)
def test_robert_data(
    mock_decide_if_blur,
    mock_var,
    mock_mean,
    mock_max,
    mock_filter2D,
    mock_np_array,
):
    mock_kernel_x = np.array([[1, 0], [0, -1]])
    mock_kernel_y = np.array([[0, 1], [-1, 0]])
    mock_gradient_x = np.array([[1, 2]])
    mock_gradient_y = np.array([[2, 4]])
    mock_np_array.side_effect = [mock_kernel_x, mock_kernel_y]
    mock_filter2D.side_effect = [mock_gradient_x, mock_gradient_y]
    assert robert_data("gray_image", [100, 200, 300]) == "return from decide_if_blur"
    mock_np_array.assert_has_calls([call([[1, 0], [0, -1]]), call([[0, 1], [-1, 0]])])
    mock_filter2D.assert_has_calls(
        [
            call("gray_image", 0, mock_kernel_x),
            call("gray_image", 0, mock_kernel_y),
        ]
    )
    mock_max.assert_called_once_with("robert_result")
    mock_mean.assert_called_once_with("robert_result")
    mock_var.assert_called_once_with("robert_result")
    mock_decide_if_blur.assert_called_once_with(12, 6, 18, [100, 200, 300])
