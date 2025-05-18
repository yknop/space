from enum import Enum
from unittest.mock import patch, call

from modules.blurring.blur_algorithm import (
    blur_disruption,
    is_blur_image,
    blur_sub_image_algorithm,
    detect_blurred_image,
)


class MockOpenImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def close(self):
        pass


class Disruptions(Enum):
    BLUR = "blur"


@patch("modules.blurring.blur_algorithm.Disruptions", Disruptions)
@patch(
    "modules.blurring.blur_algorithm.os.path.split",
    return_value=("example/image_folder", "file_name.tiff"),
)
@patch(
    "modules.blurring.blur_algorithm.os.path.splitext",
    side_effect=[("file_name", ".tiff"), ("file_name", ".tiff")],
)
@patch(
    "modules.blurring.blur_algorithm.rasterio.open", return_value=MockOpenImage(10, 20)
)
@patch("modules.blurring.blur_algorithm.is_blur_image", return_value=True)
@patch(
    "modules.blurring.blur_algorithm.create_polygon",
    return_value=[[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]],
)
@patch("modules.blurring.blur_algorithm.add_disruption")
def test_blur_disruption_on_image_blur(
    mock_add_disruption,
    mock_create_polygon,
    mock_is_blur_image,
    mock_open,
    mock_splitext,
    mock_split,
):
    blur_disruption(
        "db",
        "example/image_folder/file_name.tiff",
        1,
        "example_satellite_name",
        background_image="background_image",
    )
    mock_split.assert_called_once_with("example/image_folder/file_name.tiff")
    assert mock_splitext.call_count == 2
    mock_open.assert_called_once_with("example/image_folder/file_name.tiff")
    mock_is_blur_image.assert_called_once_with(
        "example/image_folder",
        "file_name",
        ".tiff",
        10,
        20,
        [],
        "example_satellite_name",
        "background_image",
    )
    mock_create_polygon.assert_called_once_with([])
    mock_add_disruption.assert_called_once_with(
        "db", 1, "blur", [[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]]
    )


@patch("modules.blurring.blur_algorithm.Disruptions", Disruptions)
@patch(
    "modules.blurring.blur_algorithm.os.path.split",
    return_value=("example/image_folder", "file_name.tiff"),
)
@patch(
    "modules.blurring.blur_algorithm.os.path.splitext",
    side_effect=[("file_name", ".tiff"), ("file_name", ".tiff")],
)
@patch(
    "modules.blurring.blur_algorithm.rasterio.open", return_value=MockOpenImage(10, 20)
)
@patch("modules.blurring.blur_algorithm.is_blur_image", return_value=False)
@patch(
    "modules.blurring.blur_algorithm.create_polygon",
    return_value=[[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]],
)
@patch("modules.blurring.blur_algorithm.add_disruption")
def test_blur_disruption_on_image_not_blur(
    mock_add_disruption,
    mock_create_polygon,
    mock_is_blur_image,
    mock_open,
    mock_splitext,
    mock_split,
):
    blur_disruption(
        "db",
        "example/image_folder/file_name.tiff",
        1,
        "example_satellite_name",
        background_image="background_image",
    )
    mock_split.assert_called_once_with("example/image_folder/file_name.tiff")
    assert mock_splitext.call_count == 2
    mock_open.assert_called_once_with("example/image_folder/file_name.tiff")
    mock_is_blur_image.assert_called_once_with(
        "example/image_folder",
        "file_name",
        ".tiff",
        10,
        20,
        [],
        "example_satellite_name",
        "background_image",
    )
    mock_create_polygon.assert_not_called()
    mock_add_disruption.assert_not_called()


@patch(
    "modules.blurring.blur_algorithm.get_consts_blur",
    return_value={
        "sub_image_size": 100,
        "percentage_threshold_value": 10,
        "laplacian_threshold_values": [3, 5, 7],
        "robert_threshold_values": [800, 1000, 1299],
        "sobel_threshold_values": [300, 900, 3888],
    },
)
@patch("modules.blurring.blur_algorithm.create_folder")
@patch("modules.blurring.blur_algorithm.range", return_value="return from range")
@patch("modules.blurring.blur_algorithm.product", return_value=[(1, 4), (2, 5), (3, 6)])
@patch(
    "modules.blurring.blur_algorithm.blur_sub_image_algorithm",
    side_effect=[(400, 400), (400, 0), (100, 50)],
)
@patch("modules.blurring.blur_algorithm.remove_folder")
def test_is_blur_image_when_blur(
    mock_remove_folder,
    mock_blur_sub_image_algorithm,
    mock_product,
    mock_range,
    mock_create_folder,
    mock_get_consts_blur,
):
    example_blurred_squares = []
    assert is_blur_image(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_blurred_squares,
        "example_satellite_name",
        "background_image",
    )
    mock_get_consts_blur.assert_called_once_with("example_satellite_name")
    mock_create_folder.assert_called_once_with("file_name")
    assert mock_range.call_count == 2
    mock_range.assert_has_calls(
        [
            call(0, 900, 100),
            call(0, 850, 100),
        ]
    )
    mock_product.assert_called_once_with("return from range", "return from range")
    assert mock_blur_sub_image_algorithm.call_count == 3
    mock_blur_sub_image_algorithm.assert_has_calls(
        [
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                1,
                4,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                2,
                5,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                3,
                6,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
        ]
    )
    mock_remove_folder.assert_called_once_with("file_name")


@patch(
    "modules.blurring.blur_algorithm.get_consts_blur",
    return_value={
        "sub_image_size": 100,
        "percentage_threshold_value": 10,
        "laplacian_threshold_values": [3, 5, 7],
        "robert_threshold_values": [800, 1000, 1299],
        "sobel_threshold_values": [300, 900, 3888],
    },
)
@patch("modules.blurring.blur_algorithm.create_folder")
@patch("modules.blurring.blur_algorithm.range", return_value="return from range")
@patch("modules.blurring.blur_algorithm.product", return_value=[(1, 4), (2, 5), (3, 6)])
@patch(
    "modules.blurring.blur_algorithm.blur_sub_image_algorithm",
    side_effect=[(400, 0), (400, 0), (100, 50)],
)
@patch("modules.blurring.blur_algorithm.remove_folder")
def test_is_blur_image_when_not_blur(
    mock_remove_folder,
    mock_blur_sub_image_algorithm,
    mock_product,
    mock_range,
    mock_create_folder,
    mock_get_consts_blur,
):
    example_blurred_squares = []
    assert not is_blur_image(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_blurred_squares,
        "example_satellite_name",
        "background_image",
    )
    mock_get_consts_blur.assert_called_once_with("example_satellite_name")
    mock_create_folder.assert_called_once_with("file_name")
    assert mock_range.call_count == 2
    mock_range.assert_has_calls(
        [
            call(0, 900, 100),
            call(0, 850, 100),
        ]
    )
    mock_product.assert_called_once_with("return from range", "return from range")
    assert mock_blur_sub_image_algorithm.call_count == 3
    mock_blur_sub_image_algorithm.assert_has_calls(
        [
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                1,
                4,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                2,
                5,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                3,
                6,
                example_blurred_squares,
                {
                    "sub_image_size": 100,
                    "percentage_threshold_value": 10,
                    "laplacian_threshold_values": [3, 5, 7],
                    "robert_threshold_values": [800, 1000, 1299],
                    "sobel_threshold_values": [300, 900, 3888],
                },
                "background_image",
            ),
        ]
    )
    mock_remove_folder.assert_called_once_with("file_name")


@patch("modules.blurring.blur_algorithm.min", side_effect=[400, 400])
@patch("modules.blurring.blur_algorithm.is_background_sub_image", return_value=True)
@patch(
    "modules.blurring.blur_algorithm.create_sub_image",
    return_value="file_name/file_name_0_0.tif",
)
@patch("modules.blurring.blur_algorithm.detect_blurred_image", return_value=False)
@patch("modules.blurring.blur_algorithm.remove_file")
def test_blur_sub_image_algorithm_when_is_background(
    mock_remove_file,
    mock_detect_blurred_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    blurred_squares = []
    assert blur_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        0,
        0,
        blurred_squares,
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
        "background_image",
    ) == (0, 0)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(400, 900),
            call(400, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 0, 0, 400, 400
    )
    mock_create_sub_image.assert_not_called()
    mock_detect_blurred_image.assert_not_called()
    mock_remove_file.assert_not_called()
    assert blurred_squares == []


@patch("modules.blurring.blur_algorithm.min", side_effect=[900, 850])
@patch("modules.blurring.blur_algorithm.is_background_sub_image", return_value=False)
@patch(
    "modules.blurring.blur_algorithm.create_sub_image",
    return_value="file_name/file_name_800_800.tif",
)
@patch("modules.blurring.blur_algorithm.detect_blurred_image", return_value=True)
@patch("modules.blurring.blur_algorithm.remove_file")
def test_blur_sub_image_algorithm_when_is_blurred(
    mock_remove_file,
    mock_detect_blurred_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    blurred_squares = []
    assert blur_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        800,
        800,
        blurred_squares,
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
        "background_image",
    ) == (5000, 5000)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(1200, 900),
            call(1200, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 800, 800, 100, 50
    )
    mock_create_sub_image.assert_called_once_with(
        800, 800, "file_name.tif", "example/image_folder", 100, 50
    )
    mock_detect_blurred_image.assert_called_once_with(
        "file_name/file_name_800_800.tif",
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
    )
    mock_remove_file.assert_called_once_with("file_name/file_name_800_800.tif")
    assert blurred_squares == [[(800, 800), (900, 850)]]


@patch("modules.blurring.blur_algorithm.min", side_effect=[900, 850])
@patch("modules.blurring.blur_algorithm.is_background_sub_image", return_value=False)
@patch(
    "modules.blurring.blur_algorithm.create_sub_image",
    return_value="file_name/file_name_800_800.tif",
)
@patch("modules.blurring.blur_algorithm.detect_blurred_image", return_value=False)
@patch("modules.blurring.blur_algorithm.remove_file")
def test_blur_sub_image_algorithm_when_is_not_blurred_and_not_background(
    mock_remove_file,
    mock_detect_blurred_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    blurred_squares = []
    assert blur_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        800,
        800,
        blurred_squares,
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
        "background_image",
    ) == (5000, 0)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(1200, 900),
            call(1200, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 800, 800, 100, 50
    )
    mock_create_sub_image.assert_called_once_with(
        800, 800, "file_name.tif", "example/image_folder", 100, 50
    )
    mock_detect_blurred_image.assert_called_once_with(
        "file_name/file_name_800_800.tif",
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
    )
    mock_remove_file.assert_called_once_with("file_name/file_name_800_800.tif")
    assert blurred_squares == []


@patch("modules.blurring.blur_algorithm.cv2.IMREAD_GRAYSCALE", 0)
@patch("modules.blurring.blur_algorithm.cv2.imread", return_value="image")
@patch("modules.blurring.blur_algorithm.laplacian_data", return_value=0)
@patch("modules.blurring.blur_algorithm.robert_data", return_value=1)
@patch("modules.blurring.blur_algorithm.sobel_data", return_value=1)
def test_detect_blurred_image_with_blurred_image(
    mock_sobel_data,
    mock_robert_data,
    mock_laplacian_data,
    mock_imread,
):
    assert detect_blurred_image(
        "image_name/image_name_0_0.tif",
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
    )
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_laplacian_data.assert_called_once_with("image", [3, 5, 7])
    mock_robert_data.assert_called_once_with("image", [800, 1000, 1299])
    mock_sobel_data.assert_called_once_with("image", [300, 900, 3888])


@patch("modules.blurring.blur_algorithm.cv2.IMREAD_GRAYSCALE", 0)
@patch("modules.blurring.blur_algorithm.cv2.imread", return_value="image")
@patch("modules.blurring.blur_algorithm.laplacian_data", return_value=0)
@patch("modules.blurring.blur_algorithm.robert_data", return_value=1)
@patch("modules.blurring.blur_algorithm.sobel_data", return_value=0)
def test_detect_blurred_image_with_not_blurred_image(
    mock_sobel_data,
    mock_robert_data,
    mock_laplacian_data,
    mock_imread,
):
    assert not detect_blurred_image(
        "image_name/image_name_0_0.tif",
        {
            "sub_image_size": 400,
            "percentage_threshold_value": 10,
            "laplacian_threshold_values": [3, 5, 7],
            "robert_threshold_values": [800, 1000, 1299],
            "sobel_threshold_values": [300, 900, 3888],
        },
    )
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_laplacian_data.assert_called_once_with("image", [3, 5, 7])
    mock_robert_data.assert_called_once_with("image", [800, 1000, 1299])
    mock_sobel_data.assert_called_once_with("image", [300, 900, 3888])
