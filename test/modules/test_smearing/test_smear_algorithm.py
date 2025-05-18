from enum import Enum
from unittest.mock import patch, call

from modules.smearing.smear_algorithm import (
    smear_disruption,
    arrange_to_send_smear_test,
    is_smear_image,
    smear_sub_image_algorithm,
    detect_smeared_image,
)


class MockOpenImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def close(self):
        pass


class Disruptions(Enum):
    SMEAR = "smear"


@patch("modules.smearing.smear_algorithm.Disruptions", Disruptions)
@patch(
    "modules.smearing.smear_algorithm.os.path.split",
    return_value=("example/image_folder", "file_name.tiff"),
)
@patch(
    "modules.smearing.smear_algorithm.os.path.splitext",
    side_effect=[("file_name", ".tiff"), ("file_name", ".tiff")],
)
@patch(
    "modules.smearing.smear_algorithm.rasterio.open", return_value=MockOpenImage(10, 20)
)
@patch("modules.smearing.smear_algorithm.is_smear_image", return_value=True)
@patch(
    "modules.smearing.smear_algorithm.create_polygon",
    return_value=[[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]],
)
@patch("modules.smearing.smear_algorithm.add_disruption")
def test_smear_disruption_on_smeared_image(
    mock_add_disruption,
    mock_create_polygon,
    mock_is_smear_image,
    mock_open,
    mock_splitext,
    mock_split,
):
    smear_disruption(
        "db",
        "example/image_folder/file_name.tiff",
        1,
        "example_satellite_name",
        background_image="background_image",
    )
    mock_split.assert_called_once_with("example/image_folder/file_name.tiff")
    assert mock_splitext.call_count == 2
    mock_open.assert_called_once_with("example/image_folder/file_name.tiff")
    mock_is_smear_image.assert_called_once_with(
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
        "db", 1, "smear", [[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]]
    )


@patch("modules.smearing.smear_algorithm.Disruptions", Disruptions)
@patch(
    "modules.smearing.smear_algorithm.os.path.split",
    return_value=("example/image_folder", "file_name.tiff"),
)
@patch(
    "modules.smearing.smear_algorithm.os.path.splitext",
    side_effect=[("file_name", ".tiff"), ("file_name", ".tiff")],
)
@patch(
    "modules.smearing.smear_algorithm.rasterio.open", return_value=MockOpenImage(10, 20)
)
@patch("modules.smearing.smear_algorithm.is_smear_image", return_value=False)
@patch(
    "modules.smearing.smear_algorithm.create_polygon",
    return_value=[[(0, 100), (100, 100), (100, 0), (0, 0), (0, 100)]],
)
@patch("modules.smearing.smear_algorithm.add_disruption")
def test_smear_disruption_on_not_smeared_image(
    mock_add_disruption,
    mock_create_polygon,
    mock_is_smear_image,
    mock_open,
    mock_splitext,
    mock_split,
):
    smear_disruption(
        "db",
        "example/image_folder/file_name.tiff",
        1,
        "example_satellite_name",
        background_image="background_image",
    )
    mock_split.assert_called_once_with("example/image_folder/file_name.tiff")
    assert mock_splitext.call_count == 2
    mock_open.assert_called_once_with("example/image_folder/file_name.tiff")
    mock_is_smear_image.assert_called_once_with(
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
    "modules.smearing.smear_algorithm.get_consts_smear",
    return_value={
        "size": 100,
        "percentage_threshold_value": 10,
        "threshold_value": 1200,
    },
)
@patch("modules.smearing.smear_algorithm.create_folder")
@patch(
    "modules.smearing.smear_algorithm.arrange_to_send_smear_test",
    return_value=(8000, 10000),
)
@patch("modules.smearing.smear_algorithm.remove_folder")
def test_is_smear_image_when_smear(
    mock_remove_folder,
    mock_arrange_to_send_smear_test,
    mock_create_folder,
    mock_get_consts_smear,
):
    example_smeared_squares = []
    assert is_smear_image(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_smeared_squares,
        "example_satellite_name",
        "background_image",
    )
    mock_get_consts_smear.assert_called_once_with("example_satellite_name")
    mock_create_folder.assert_called_once_with("file_name")
    mock_arrange_to_send_smear_test.assert_called_once_with(
        {"size": 100, "percentage_threshold_value": 10, "threshold_value": 1200},
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_smeared_squares,
        "background_image",
    )
    mock_remove_folder.assert_called_once_with("file_name")


@patch(
    "modules.smearing.smear_algorithm.get_consts_smear",
    return_value={
        "size": 100,
        "percentage_threshold_value": 10,
        "threshold_value": 1200,
    },
)
@patch("modules.smearing.smear_algorithm.create_folder")
@patch(
    "modules.smearing.smear_algorithm.arrange_to_send_smear_test",
    return_value=(10, 10000),
)
@patch("modules.smearing.smear_algorithm.remove_folder")
def test_is_smear_image_when_not_smear(
    mock_remove_folder,
    mock_arrange_to_send_smear_test,
    mock_create_folder,
    mock_get_consts_smear,
):
    example_smeared_squares = []
    assert not is_smear_image(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_smeared_squares,
        "example_satellite_name",
        "background_image",
    )
    mock_get_consts_smear.assert_called_once_with("example_satellite_name")
    mock_create_folder.assert_called_once_with("file_name")
    mock_arrange_to_send_smear_test.assert_called_once_with(
        {"size": 100, "percentage_threshold_value": 10, "threshold_value": 1200},
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        example_smeared_squares,
        "background_image",
    )
    mock_remove_folder.assert_called_once_with("file_name")


@patch("modules.smearing.smear_algorithm.range", return_value="return from range")
@patch(
    "modules.smearing.smear_algorithm.product", return_value=[(1, 4), (2, 5), (3, 6)]
)
@patch(
    "modules.smearing.smear_algorithm.smear_sub_image_algorithm",
    side_effect=[(400, 400), (400, 0), (100, 50)],
)
def test_arrange_to_send_smear_test(
    mock_smear_sub_image_algorithm,
    mock_product,
    mock_range,
):
    assert arrange_to_send_smear_test(
        {"size": 100},
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        "example_smeared_squares",
        "background_image",
    )
    assert mock_range.call_count == 2
    mock_range.assert_has_calls(
        [
            call(0, 900, 100),
            call(0, 850, 100),
        ]
    )
    mock_product.assert_called_once_with("return from range", "return from range")
    assert mock_smear_sub_image_algorithm.call_count == 3
    mock_smear_sub_image_algorithm.assert_has_calls(
        [
            call(
                "example/image_folder",
                "file_name",
                ".tif",
                900,
                850,
                1,
                4,
                "example_smeared_squares",
                {"size": 100},
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
                "example_smeared_squares",
                {"size": 100},
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
                "example_smeared_squares",
                {"size": 100},
                "background_image",
            ),
        ]
    )


@patch("modules.smearing.smear_algorithm.min", side_effect=[400, 400])
@patch("modules.smearing.smear_algorithm.is_background_sub_image", return_value=True)
@patch(
    "modules.smearing.smear_algorithm.create_sub_image",
    return_value="file_name/file_name_0_0.tif",
)
@patch("modules.smearing.smear_algorithm.detect_smeared_image", return_value=False)
@patch("modules.smearing.smear_algorithm.remove_file")
def test_smear_sub_image_algorithm_when_is_background(
    mock_remove_file,
    mock_detect_smeared_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    smeared_squares = []
    assert smear_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        0,
        0,
        smeared_squares,
        {"size": 100, "threshold_value": 1200},
        "background_image",
    ) == (0, 0)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(100, 900),
            call(100, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 0, 0, 400, 400
    )
    mock_create_sub_image.assert_not_called()
    mock_detect_smeared_image.assert_not_called()
    mock_remove_file.assert_not_called()
    assert smeared_squares == []


@patch("modules.smearing.smear_algorithm.min", side_effect=[900, 850])
@patch("modules.smearing.smear_algorithm.is_background_sub_image", return_value=False)
@patch(
    "modules.smearing.smear_algorithm.create_sub_image",
    return_value="file_name/file_name_800_800.tif",
)
@patch("modules.smearing.smear_algorithm.detect_smeared_image", return_value=True)
@patch("modules.smearing.smear_algorithm.remove_file")
def test_smear_sub_image_algorithm_when_is_smeared(
    mock_remove_file,
    mock_detect_smeared_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    smeared_squares = []
    assert smear_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        800,
        800,
        smeared_squares,
        {"size": 100, "threshold_value": 1200},
        "background_image",
    ) == (5000, 5000)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(900, 900),
            call(900, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 800, 800, 100, 50
    )
    mock_create_sub_image.assert_called_once_with(
        800, 800, "file_name.tif", "example/image_folder", 100, 50
    )
    mock_detect_smeared_image.assert_called_once_with(
        "file_name/file_name_800_800.tif", {"size": 100, "threshold_value": 1200}
    )
    mock_remove_file.assert_called_once_with("file_name/file_name_800_800.tif")
    assert smeared_squares == [[(800, 800), (900, 850)]]


@patch("modules.smearing.smear_algorithm.min", side_effect=[900, 850])
@patch("modules.smearing.smear_algorithm.is_background_sub_image", return_value=False)
@patch(
    "modules.smearing.smear_algorithm.create_sub_image",
    return_value="file_name/file_name_800_800.tif",
)
@patch("modules.smearing.smear_algorithm.detect_smeared_image", return_value=False)
@patch("modules.smearing.smear_algorithm.remove_file")
def test_smear_sub_image_algorithm_when_is_not_smeared_and_not_background(
    mock_remove_file,
    mock_detect_smeared_image,
    mock_create_sub_image,
    mock_is_background_sub_image,
    mock_min,
):
    smeared_squares = []
    assert smear_sub_image_algorithm(
        "example/image_folder",
        "file_name",
        ".tif",
        900,
        850,
        800,
        800,
        smeared_squares,
        {"size": 100, "threshold_value": 1200},
        "background_image",
    ) == (5000, 0)
    assert mock_min.call_count == 2
    mock_min.assert_has_calls(
        [
            call(900, 900),
            call(900, 850),
        ]
    )
    mock_is_background_sub_image.assert_called_once_with(
        "background_image", 800, 800, 100, 50
    )
    mock_create_sub_image.assert_called_once_with(
        800, 800, "file_name.tif", "example/image_folder", 100, 50
    )
    mock_detect_smeared_image.assert_called_once_with(
        "file_name/file_name_800_800.tif", {"size": 100, "threshold_value": 1200}
    )
    mock_remove_file.assert_called_once_with("file_name/file_name_800_800.tif")
    assert smeared_squares == []


@patch("modules.smearing.smear_algorithm.cv2.imread", return_value="image")
@patch("modules.smearing.smear_algorithm.compare_decay", return_value=1100)
@patch("modules.smearing.smear_algorithm.is_smooth_region", return_value=True)
def test_detect_smooth_image(
    mock_is_smooth_region,
    mock_compare_decay,
    mock_imread,
):
    assert not detect_smeared_image("image_name/image_name_0_0.tif", 1200)
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_compare_decay.assert_called_once_with("image")
    mock_is_smooth_region.assert_called_once_with("image", 1200)


@patch("modules.smearing.smear_algorithm.cv2.imread", return_value="image")
@patch("modules.smearing.smear_algorithm.compare_decay", return_value=None)
@patch("modules.smearing.smear_algorithm.is_smooth_region")
def test_detect_small_image(
    mock_is_smooth_region,
    mock_compare_decay,
    mock_imread,
):
    assert not detect_smeared_image("image_name/image_name_0_0.tif", 1200)
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_compare_decay.assert_called_once_with("image")
    mock_is_smooth_region.assert_not_called()


@patch("modules.smearing.smear_algorithm.cv2.imread", return_value="image")
@patch("modules.smearing.smear_algorithm.compare_decay", return_value=1100)
@patch("modules.smearing.smear_algorithm.is_smooth_region", return_value=False)
def test_detect_smear_image(
    mock_is_smooth_region,
    mock_compare_decay,
    mock_imread,
):
    assert detect_smeared_image(
        "image_name/image_name_0_0.tif", {"threshold_value": 1200}
    )
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_compare_decay.assert_called_once_with("image")
    mock_is_smooth_region.assert_called_once_with("image", {"threshold_value": 1200})


@patch("modules.smearing.smear_algorithm.cv2.imread", return_value="image")
@patch("modules.smearing.smear_algorithm.compare_decay", return_value=1300)
@patch("modules.smearing.smear_algorithm.is_smooth_region", return_value=False)
def test_detect_not_smear_image(
    mock_is_smooth_region,
    mock_compare_decay,
    mock_imread,
):
    assert not detect_smeared_image(
        "image_name/image_name_0_0.tif", {"threshold_value": 1200}
    )
    mock_imread.assert_called_once_with("image_name/image_name_0_0.tif", 0)
    mock_compare_decay.assert_called_once_with("image")
    mock_is_smooth_region.assert_called_once_with("image", {"threshold_value": 1200})
