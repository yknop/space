from unittest.mock import patch

from modules.blurring.laplacian_algorithm import laplacian_data


@patch("modules.blurring.laplacian_algorithm.cv2.CV_64F", 0)
@patch(
    "modules.blurring.laplacian_algorithm.cv2.Laplacian",
    return_value="return_laplacian",
)
@patch(
    "modules.blurring.laplacian_algorithm.np.absolute",
    return_value="return_absolute",
)
@patch(
    "modules.blurring.laplacian_algorithm.np.uint8",
    return_value="laplacian",
)
@patch("modules.blurring.laplacian_algorithm.np.max", return_value=12)
@patch("modules.blurring.laplacian_algorithm.np.mean", return_value=6.0)
@patch("modules.blurring.laplacian_algorithm.np.var", return_value=18.0)
@patch(
    "modules.blurring.laplacian_algorithm.decide_if_blur",
    return_value="return from decide_if_blur",
)
def test_laplacian_data(
    mock_decide_if_blur,
    mock_var,
    mock_mean,
    mock_max,
    mock_uint8,
    mock_absolute,
    mock_laplacian,
):
    assert laplacian_data("gray_image", [100, 200, 300]) == "return from decide_if_blur"
    mock_laplacian.assert_called_once_with("gray_image", 0)
    mock_absolute.assert_called_once_with("return_laplacian")
    mock_uint8.assert_called_once_with("return_absolute")
    mock_max.assert_called_once_with("laplacian")
    mock_mean.assert_called_once_with("laplacian")
    mock_var.assert_called_once_with("laplacian")
    mock_decide_if_blur.assert_called_once_with(12, 6, 18, [100, 200, 300])
