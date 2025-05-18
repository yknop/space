from unittest.mock import patch, call, Mock
import pytest
import numpy as np


from modules.manage_images import (
    get_image_file,
    convert_ntf_image,
    create_sub_image,
    read_sub_image,
    get_new_profile,
    save_sub_image,
    create_background_image,
    fill_background_pixels,
    fill_background_pixel,
    change_background_pixels,
    change_pixel,
    is_correct_position,
    is_background_sub_image,
)


class MockImage:
    def __init__(self):
        self.profile = {"driver": "NTif"}
        self.transform = "transform"
        self.width = 9000
        self.height = 8000

    def read(self, window):
        return "sub_image from read"

    def close(self):
        pass


@patch(
    "modules.manage_images.convert_ntf_image",
    return_value="return value from convert_ntf_image",
)
def test_get_image_file_for_blacksky_image(mock_convert_ntf_image):
    assert (
        get_image_file("folder_path", "BlackSky")
        == "return value from convert_ntf_image"
    )
    mock_convert_ntf_image.assert_called_once_with("folder_path")


@patch(
    "modules.manage_images.convert_ntf_image",
    return_value="return value from convert_ntf_image",
)
def test_get_image_file_for_another_satellite_image(mock_convert_ntf_image):
    with pytest.raises(Exception, match="Unsupported satellite name."):
        get_image_file("folder_path", "another_satellite")
    mock_convert_ntf_image.assert_not_called()


@patch(
    "modules.manage_images.get_ntf_file_and_folder_path",
    return_value=("example_image_name.ntf", "folder_1/folder_2/folder_3"),
)
@patch(
    "modules.manage_images.os.path.splitext",
    return_value=("example_image_name", ".ntf"),
)
@patch(
    "modules.manage_images.os.path.join",
    side_effect=[
        "folder_1/folder_2/folder_3/example_image_name-temp.tif",
        "folder_1/folder_2/folder_3/example_image_name.tif",
        "folder_1/folder_2/folder_3/example_image_name.ntf",
    ],
)
@patch("modules.manage_images.convert_ntf_to_tif")
@patch("modules.manage_images.convert_image_to_8_bit")
@patch("modules.manage_images.remove_file")
def test_convert_ntf_image(
    mock_remove_file,
    mock_convert_image_to_8_bit,
    mock_convert_ntf_to_tif,
    mock_join,
    mock_splitext,
    mock_get_ntf_file_and_folder_path,
):
    assert convert_ntf_image("folder_1") == (
        "example_image_name.tif",
        "folder_1/folder_2/folder_3/example_image_name.tif",
    )
    mock_get_ntf_file_and_folder_path.assert_called_once_with("folder_1")
    mock_splitext.assert_called_once_with("example_image_name.ntf")
    assert mock_join.call_count == 3
    mock_join.assert_has_calls(
        [
            call("folder_1/folder_2/folder_3", "example_image_name-temp.tif"),
            call("folder_1/folder_2/folder_3", "example_image_name.tif"),
            call("folder_1/folder_2/folder_3", "example_image_name.ntf"),
        ]
    )
    mock_convert_ntf_to_tif.assert_called_once_with(
        "folder_1/folder_2/folder_3/example_image_name.ntf",
        "folder_1/folder_2/folder_3/example_image_name-temp.tif",
    )
    mock_convert_image_to_8_bit.assert_called_once_with(
        "folder_1/folder_2/folder_3/example_image_name-temp.tif",
        "folder_1/folder_2/folder_3/example_image_name.tif",
    )
    mock_remove_file.assert_called_once_with(
        "folder_1/folder_2/folder_3/example_image_name-temp.tif"
    )


@patch("modules.manage_images.os.path.splitext", return_value=("image_name", ".ntf"))
@patch(
    "modules.manage_images.os.path.join",
    side_effect=["img_dir/image_name.ntf", "image_name/image_name_800_1200.tif"],
)
@patch(
    "modules.manage_images.read_sub_image",
    return_value=("sub_image", "profile_sub_image"),
)
@patch("modules.manage_images.save_sub_image")
def test_create_sub_image(
    mock_save_sub_image, mock_read_sub_image, mock_join, mock_splitext
):
    assert (
        create_sub_image(800, 1200, "image_name.ntf", "img_dir", 400, 400)
        == "image_name/image_name_800_1200.tif"
    )
    mock_splitext.assert_called_once_with("image_name.ntf")
    assert mock_join.call_count == 2
    mock_join.assert_has_calls(
        [
            call("img_dir", "image_name.ntf"),
            call("image_name", "image_name_800_1200.tif"),
        ]
    )
    mock_read_sub_image.assert_called_once_with(
        "img_dir/image_name.ntf", 800, 1200, 400, 400
    )
    mock_save_sub_image.assert_called_once_with(
        "image_name/image_name_800_1200.tif", "sub_image", "profile_sub_image"
    )


@patch("modules.manage_images.os.path.splitext", return_value=("image_name", ".ntf"))
@patch(
    "modules.manage_images.os.path.join",
    side_effect=["img_dir/image_name.ntf", "image_name/image_name_800_1200.tif"],
)
@patch(
    "modules.manage_images.read_sub_image",
    side_effect=Exception("Exception in read sub image."),
)
@patch("modules.manage_images.save_sub_image")
def test_create_sub_image_when_read_sub_image_raise_exception(
    mock_save_sub_image, mock_read_sub_image, mock_join, mock_splitext
):
    with pytest.raises(
        Exception,
        match="An error occured in create_sub_image: Exception in read sub image.",
    ):
        create_sub_image(800, 1200, "image_name.ntf", "img_dir", 400, 400)
    mock_splitext.assert_called_once_with("image_name.ntf")
    assert mock_join.call_count == 2
    mock_join.assert_has_calls(
        [
            call("img_dir", "image_name.ntf"),
            call("image_name", "image_name_800_1200.tif"),
        ]
    )
    mock_read_sub_image.assert_called_once_with(
        "img_dir/image_name.ntf", 800, 1200, 400, 400
    )
    mock_save_sub_image.assert_not_called()


@patch("modules.manage_images.Window", return_value="window")
@patch("modules.manage_images.rasterio.open", return_value=MockImage())
@patch(
    "modules.manage_images.get_new_profile",
    return_value={"key": "return from get_new_profile"},
)
def test_read_sub_image(mock_get_new_profile, mock_open, mock_window):
    assert read_sub_image("img_path", 800, 1200, 400, 400) == (
        "sub_image from read",
        {"key": "return from get_new_profile"},
    )
    mock_window.assert_called_once_with(800, 1200, 400, 400)
    mock_open.assert_called_once_with("img_path")
    mock_get_new_profile.assert_called_once_with(
        {"driver": "NTif"}, 400, 400, "window", "transform"
    )


@patch("modules.manage_images.Window", return_value="window")
@patch(
    "modules.manage_images.rasterio.open",
    side_effect=Exception("Exception in open image path."),
)
@patch(
    "modules.manage_images.get_new_profile",
    return_value={"key": "return from get_new_profile"},
)
def test_read_sub_image_when_open_image_raise_exception(
    mock_get_new_profile, mock_open, mock_window
):
    with pytest.raises(
        Exception,
        match="An error occured when read sub image: Exception in open image path.",
    ):
        read_sub_image("img_path", 800, 1200, 400, 400)
    mock_window.assert_called_once_with(800, 1200, 400, 400)
    mock_open.assert_called_once_with("img_path")
    mock_get_new_profile.assert_not_called()


@patch(
    "modules.manage_images.rasterio.windows.transform",
    return_value="return from rasterio transform",
)
def test_get_new_profile(mock_windows_transform):
    assert get_new_profile(
        {"driver": "NTif", "height": 30000, "width": 40000, "key": "value"},
        400,
        400,
        "window",
        "transform",
    ) == {
        "driver": "GTiff",
        "height": 400,
        "width": 400,
        "transform": "return from rasterio transform",
        "key": "value",
    }
    mock_windows_transform.assert_called_once_with("window", "transform")


@patch("modules.manage_images.rasterio.open")
def test_save_sub_image(mock_open):
    mock_dest_image = Mock()
    mock_open.return_value = mock_dest_image
    save_sub_image("sub_image_path", "sub_image", {"key": "value", "hello": "world"})
    mock_open.assert_called_once_with("sub_image_path", "w", key="value", hello="world")
    mock_dest_image.write.assert_called_once_with("sub_image")
    mock_dest_image.close.assert_called_once_with()


@patch(
    "modules.manage_images.rasterio.open",
    side_effect=Exception("Exception in open image path."),
)
def test_save_sub_image_when_open_image_raise_exception(mock_open):
    mock_dest_image = Mock()
    mock_open.return_value = mock_dest_image
    with pytest.raises(
        Exception,
        match="An error occured when write sub image: Exception in open image path.",
    ):
        save_sub_image(
            "sub_image_path", "sub_image", {"key": "value", "hello": "world"}
        )
    mock_open.assert_called_once_with("sub_image_path", "w", key="value", hello="world")
    mock_dest_image.write.assert_not_called()
    mock_dest_image.close.assert_not_called()


@patch("modules.manage_images.cv2.IMREAD_GRAYSCALE", 1)
@patch("modules.manage_images.cv2.imread")
@patch("modules.manage_images.len", return_value=5)
@patch("modules.manage_images.np.zeros", return_value="return from np.zeros")
@patch("modules.manage_images.fill_background_pixels")
def test_create_background_image(
    mock_fill_background_pixels, mock_zeros, mock_len, mock_imread
):
    image = np.array(
        [
            [2, 3, 3, 3, 2],
            [2, 3, 3, 3, 2],
            [2, 3, 3, 3, 2],
            [2, 3, 3, 3, 2],
            [2, 3, 3, 3, 2],
        ]
    )
    mock_imread.return_value = image
    create_background_image("image_path") == "return from np.zeros"
    mock_imread.assert_called_once_with("image_path", 1)
    assert mock_len.call_count == 2
    mock_zeros.assert_called_once_with((5, 5))
    mock_fill_background_pixels.assert_called_once_with(image, "return from np.zeros")


@patch("modules.manage_images.fill_background_pixel")
def test_fill_background_pixels(mock_fill_background_pixel):
    image = np.zeros((5, 4))
    background_image = np.zeros((5, 4))
    fill_background_pixels(image, background_image)
    assert mock_fill_background_pixel.call_count == 18
    mock_fill_background_pixel.assert_has_calls(
        [
            call(image, background_image, [], 0, 0),
            call(image, background_image, [], 0, 3),
            call(image, background_image, [], 1, 0),
            call(image, background_image, [], 1, 3),
            call(image, background_image, [], 2, 0),
            call(image, background_image, [], 2, 3),
            call(image, background_image, [], 3, 0),
            call(image, background_image, [], 3, 3),
            call(image, background_image, [], 4, 0),
            call(image, background_image, [], 4, 3),
            call(image, background_image, [], 0, 0),
            call(image, background_image, [], 4, 0),
            call(image, background_image, [], 0, 1),
            call(image, background_image, [], 4, 1),
            call(image, background_image, [], 0, 2),
            call(image, background_image, [], 4, 2),
            call(image, background_image, [], 0, 3),
            call(image, background_image, [], 4, 3),
        ]
    )


@patch("modules.manage_images.change_background_pixels")
def test_fill_background_pixel_when_pixel_is_background(mock_change_background_pixels):
    image = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    background_image = np.zeros((5, 5))
    fill_background_pixel(image, background_image, [], 0, 0)
    mock_change_background_pixels.assert_called_once_with(
        image, background_image, [(0, 0)]
    )


@patch("modules.manage_images.change_background_pixels")
def test_fill_background_pixel_when_pixel_already_set_in_background_image(
    mock_change_background_pixels,
):
    image = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    background_image = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    fill_background_pixel(image, background_image, [], 0, 3)
    mock_change_background_pixels.assert_not_called()


@patch("modules.manage_images.change_background_pixels")
def test_fill_background_pixel_when_pixel_not_background(mock_change_background_pixels):
    image = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    background_image = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    fill_background_pixel(image, background_image, [], 1, 1)
    mock_change_background_pixels.assert_not_called()


@patch("modules.manage_images.change_pixel")
def test_change_background_pixels(mock_change_pixel):
    image = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    background_image = np.array(
        [
            [1, 1, 0, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 0, 1, 1],
        ]
    )
    background_pixels = [(0, 2), (0, 3), (4, 2)]
    change_background_pixels(image, background_image, background_pixels)
    assert mock_change_pixel.call_count == 8
    mock_change_pixel.assert_has_calls(
        [
            call(image, background_image, background_pixels, 4, 1),
            call(image, background_image, background_pixels, 4, 3),
            call(image, background_image, background_pixels, 3, 2),
            call(image, background_image, background_pixels, 5, 2),
            call(image, background_image, background_pixels, 0, 1),
            call(image, background_image, background_pixels, 0, 3),
            call(image, background_image, background_pixels, -1, 2),
            call(image, background_image, background_pixels, 1, 2),
        ]
    )


@patch(
    "modules.manage_images.is_correct_position", side_effect=[True, False, True, True]
)
def test_change_pixel(mock_is_correct_position):
    image = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    background_image = np.array(
        [
            [1, 1, 0, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 0, 1, 1],
        ]
    )
    background_pixels = []
    change_pixel(image, background_image, background_pixels, 1, 1)
    assert background_pixels == []
    change_pixel(image, background_image, background_pixels, 0, -1)
    assert background_pixels == []
    change_pixel(image, background_image, background_pixels, 0, 2)
    assert background_pixels == [(0, 2)]
    change_pixel(image, background_image, background_pixels, 0, 3)
    assert background_pixels == [(0, 2)]
    assert mock_is_correct_position.call_count == 4
    mock_is_correct_position.assert_has_calls(
        [
            call(background_image, 1, 1),
            call(background_image, 0, -1),
            call(background_image, 0, 2),
            call(background_image, 0, 3),
        ]
    )


def test_is_correct_position():
    background_image = np.zeros((5, 5))
    assert is_correct_position(background_image, 0, 0)
    assert is_correct_position(background_image, 4, 4)
    assert not is_correct_position(background_image, 4, 5)
    assert not is_correct_position(background_image, -1, 3)
    assert not is_correct_position(background_image, 5, 0)
    assert not is_correct_position(background_image, 2, -2)


def test_is_background_sub_image():
    background_image = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    assert is_background_sub_image(background_image, 1, 1, 4, 4)
    assert not is_background_sub_image(background_image, 1, 1, 3, 3)
