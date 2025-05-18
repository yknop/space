from unittest.mock import patch, call
import pytest

from utils.files.manage_folders import (
    create_folder,
    remove_folder,
    remove_file,
    polygon_image_path,
    get_metadata_json_file,
    is_metadata_json_file,
    get_file_path_by_extension,
    get_file_recursive,
    get_file_path,
    get_file_path_from_sub_folders,
    get_tif_file_and_file_path,
    is_tif_file,
    get_ntf_file_and_folder_path,
    is_correct_ntf_file,
)


def mock_function(file):
    pass


def mock_function_check_if_file_endswith_tif(file):
    return file.endswith("tif")


@patch("os.path.isdir")
@patch("os.mkdir")
def test_create_folder(mock_mkdir, mock_isdir):
    mock_isdir.return_value = False
    folder_name = "test_folder"
    create_folder(folder_name)
    mock_isdir.assert_called_with(f"./{folder_name}")
    mock_mkdir.assert_called_with(f"./{folder_name}")


@patch("modules.manage_folders.os.path.isdir", return_value=True)
@patch("modules.manage_folders.remove_folder")
@patch("modules.manage_folders.os.mkdir")
def test_create_folder_when_not_exist(mock_mkdir, mock_remove_folder, mock_isdir):
    create_folder("folder_name")
    mock_isdir.assert_called_once_with("./folder_name")
    mock_remove_folder.assert_called_once_with("folder_name")
    mock_mkdir.assert_called_once_with("./folder_name")


@patch("shutil.rmtree")
def test_remove_folder(mock_rmtree):
    folder_name = "test_folder"
    remove_folder(folder_name)
    mock_rmtree.assert_called_with(folder_name)


@patch(
    "modules.manage_folders.shutil.rmtree",
    side_effect=OSError("Raise exception from shutil.rmtree."),
)
def test_remove_folder_raise_exception(mock_rmtree):
    with pytest.raises(OSError, match="Raise exception from shutil.rmtree."):
        remove_folder("folder_name")
    mock_rmtree.assert_called_once_with("folder_name")


@patch("modules.manage_folders.os.path.exists", side_effect=[True, False])
@patch("modules.manage_folders.os.remove")
def test_remove_file(mock_remove, mock_path_exists):
    remove_file("file_name_example_1")
    remove_file("file_name_example_2")
    mock_path_exists.assert_has_calls(
        [
            call("file_name_example_1"),
            call("file_name_example_2"),
        ]
    )
    mock_remove.assert_called_once_with("file_name_example_1")


def test_polygon_image_path():
    src_path = "app/images/src/test.png"
    folder_name = "polygons/testing"
    new_path = polygon_image_path(src_path, folder_name)
    assert new_path == "app/images/polygons/testing/test.png"


@patch(
    "modules.manage_folders.get_file_path_by_extension",
    return_value="return from get_file_path_by_extension",
)
@patch("modules.manage_folders.is_metadata_json_file", mock_function)
def test_get_metadata_json_file(mock_get_file_path_by_extension):
    assert (
        get_metadata_json_file("folder_path")
        == "return from get_file_path_by_extension"
    )
    mock_get_file_path_by_extension.assert_called_once_with(
        "folder_path", "metadata.json", mock_function
    )


def test_is_metadata_json_file():
    assert is_metadata_json_file("example_file_metadata.json")
    assert not is_metadata_json_file("example_file.json")


@patch(
    "modules.manage_folders.get_file_recursive",
    return_value="folder_path/file_path.tif",
)
def test_get_file_path_by_extension_when_exist_file(mock_get_file_recursive):
    assert (
        get_file_path_by_extension("folder_path", ".tif", mock_function)
        == "folder_path/file_path.tif"
    )
    mock_get_file_recursive.assert_called_once_with("folder_path", mock_function)


@patch("modules.manage_folders.get_file_recursive", return_value=None)
def test_get_file_path_by_extension_when_file_not_exist(mock_get_file_recursive):
    with pytest.raises(Exception, match=".tif file was not found."):
        get_file_path_by_extension("folder_path", ".tif", mock_function)
    mock_get_file_recursive.assert_called_once_with("folder_path", mock_function)


@patch("modules.manage_folders.get_file_path", return_value="folder_path/file_path.tif")
@patch(
    "modules.manage_folders.get_file_path_from_sub_folders",
    return_value="return value from get_file_path_from_sub_folders",
)
def test_get_file_recursive_when_file_exist_in_the_base_folder_path(
    mock_get_file_path_from_sub_folders, mock_get_file_path
):
    assert (
        get_file_recursive("folder_path", mock_function) == "folder_path/file_path.tif"
    )
    mock_get_file_path.assert_called_once_with("folder_path", mock_function)
    mock_get_file_path_from_sub_folders.assert_not_called()


@patch("modules.manage_folders.get_file_path", return_value=None)
@patch(
    "modules.manage_folders.get_file_path_from_sub_folders",
    return_value="return value from get_file_path_from_sub_folders",
)
def test_get_file_recursive_when_file_not_exist_in_the_base_folder_path(
    mock_get_file_path_from_sub_folders, mock_get_file_path
):
    assert (
        get_file_recursive("folder_path", mock_function)
        == "return value from get_file_path_from_sub_folders"
    )
    mock_get_file_path.assert_called_once_with("folder_path", mock_function)
    mock_get_file_path_from_sub_folders.assert_called_once_with(
        "folder_path", mock_function
    )


@patch(
    "modules.manage_folders.os.listdir",
    return_value=["folder_1", "file_not_tif.txt", "example_tif_file.tif", "folder_2"],
)
@patch(
    "modules.manage_folders.os.path.join",
    side_effect=[
        "folder_path/folder_1",
        "folder_path/file_not_tif.txt",
        "folder_path/example_tif_file.tif",
        "folder_path/folder_2",
    ],
)
@patch("modules.manage_folders.os.path.isfile", side_effect=[False, True, True, False])
def test_get_file_path_when_exist_file(mock_isfile, mock_join, mock_listdir):
    assert (
        get_file_path("folder_path", mock_function_check_if_file_endswith_tif)
        == "folder_path/example_tif_file.tif"
    )
    mock_listdir.assert_called_once_with("folder_path")
    assert mock_join.call_count == 3
    mock_join.assert_has_calls(
        [
            call("folder_path", "folder_1"),
            call("folder_path", "file_not_tif.txt"),
            call("folder_path", "example_tif_file.tif"),
        ]
    )
    assert mock_isfile.call_count == 3
    mock_isfile.assert_has_calls(
        [
            call("folder_path/folder_1"),
            call("folder_path/file_not_tif.txt"),
            call("folder_path/example_tif_file.tif"),
        ]
    )


@patch(
    "modules.manage_folders.os.listdir",
    return_value=["folder_1", "file_not_tif.txt", "another_txt_file.txt", "folder_2"],
)
@patch(
    "modules.manage_folders.os.path.join",
    side_effect=[
        "folder_path/folder_1",
        "folder_path/file_not_tif.txt",
        "folder_path/another_txt_file.txt",
        "folder_path/folder_2",
    ],
)
@patch("modules.manage_folders.os.path.isfile", side_effect=[False, True, True, False])
def test_get_file_path_when_file_not_exist(mock_isfile, mock_join, mock_listdir):
    assert not get_file_path("folder_path", mock_function_check_if_file_endswith_tif)
    mock_listdir.assert_called_once_with("folder_path")
    assert mock_join.call_count == 4
    mock_join.assert_has_calls(
        [
            call("folder_path", "folder_1"),
            call("folder_path", "file_not_tif.txt"),
            call("folder_path", "another_txt_file.txt"),
            call("folder_path", "folder_2"),
        ]
    )
    assert mock_isfile.call_count == 4
    mock_isfile.assert_has_calls(
        [
            call("folder_path/folder_1"),
            call("folder_path/file_not_tif.txt"),
            call("folder_path/another_txt_file.txt"),
            call("folder_path/folder_2"),
        ]
    )


@patch(
    "modules.manage_folders.os.listdir",
    return_value=[
        "folder_1",
        "file_not_tif.txt",
        "folder_2",
        "another_txt_file.txt",
        "folder_3",
    ],
)
@patch(
    "modules.manage_folders.os.path.join",
    side_effect=[
        "folder_path/folder_1",
        "folder_path/file_not_tif.txt",
        "folder_path/folder_2",
        "folder_path/another_txt_file.txt",
        "folder_path/folder_3",
    ],
)
@patch(
    "modules.manage_folders.os.path.isdir", side_effect=[True, False, True, False, True]
)
@patch(
    "modules.manage_folders.get_file_recursive",
    side_effect=[None, "folder_path/folder_2/example_tif_file.tif", None],
)
def test_get_file_path_from_sub_folders_when_file_exist(
    mock_get_file_recursive, mock_isdir, mock_join, mock_listdir
):
    assert (
        get_file_path_from_sub_folders("folder_path", mock_function)
        == "folder_path/folder_2/example_tif_file.tif"
    )
    mock_listdir.assert_called_once_with("folder_path")
    assert mock_join.call_count == 3
    mock_join.assert_has_calls(
        [
            call("folder_path", "folder_1"),
            call("folder_path", "file_not_tif.txt"),
            call("folder_path", "folder_2"),
        ]
    )
    assert mock_isdir.call_count == 3
    mock_isdir.assert_has_calls(
        [
            call("folder_path/folder_1"),
            call("folder_path/file_not_tif.txt"),
            call("folder_path/folder_2"),
        ]
    )
    assert mock_get_file_recursive.call_count == 2
    mock_get_file_recursive.assert_has_calls(
        [
            call("folder_path/folder_1", mock_function),
            call("folder_path/folder_2", mock_function),
        ]
    )


@patch(
    "modules.manage_folders.os.listdir",
    return_value=[
        "folder_1",
        "file_not_tif.txt",
        "folder_2",
        "another_txt_file.txt",
        "folder_3",
    ],
)
@patch(
    "modules.manage_folders.os.path.join",
    side_effect=[
        "folder_path/folder_1",
        "folder_path/file_not_tif.txt",
        "folder_path/folder_2",
        "folder_path/another_txt_file.txt",
        "folder_path/folder_3",
    ],
)
@patch(
    "modules.manage_folders.os.path.isdir", side_effect=[True, False, True, False, True]
)
@patch("modules.manage_folders.get_file_recursive", side_effect=[None, None, None])
def test_get_file_path_from_sub_folders_when_file_not_exist(
    mock_get_file_recursive, mock_isdir, mock_join, mock_listdir
):
    assert not get_file_path_from_sub_folders("folder_path", mock_function)
    mock_listdir.assert_called_once_with("folder_path")
    assert mock_join.call_count == 5
    mock_join.assert_has_calls(
        [
            call("folder_path", "folder_1"),
            call("folder_path", "file_not_tif.txt"),
            call("folder_path", "folder_2"),
            call("folder_path", "another_txt_file.txt"),
            call("folder_path", "folder_3"),
        ]
    )
    assert mock_isdir.call_count == 5
    mock_isdir.assert_has_calls(
        [
            call("folder_path/folder_1"),
            call("folder_path/file_not_tif.txt"),
            call("folder_path/folder_2"),
            call("folder_path/another_txt_file.txt"),
            call("folder_path/folder_3"),
        ]
    )
    assert mock_get_file_recursive.call_count == 3
    mock_get_file_recursive.assert_has_calls(
        [
            call("folder_path/folder_1", mock_function),
            call("folder_path/folder_2", mock_function),
            call("folder_path/folder_3", mock_function),
        ]
    )


@patch(
    "modules.manage_folders.get_file_path_by_extension",
    return_value="folder_1/folder_2/folder_3/example_tif_file.tif",
)
@patch("modules.manage_folders.is_tif_file", mock_function)
def test_get_tif_file_and_file_path(mock_get_file_path_by_extension):
    assert get_tif_file_and_file_path("folder_1") == (
        "example_tif_file.tif",
        "folder_1/folder_2/folder_3/example_tif_file.tif",
    )
    mock_get_file_path_by_extension.assert_called_once_with(
        "folder_1", ".tif", mock_function
    )


def test_is_tif_file():
    assert is_tif_file("example_tif_file.tif")
    assert not is_tif_file("example_not_tif_file.txt")


@patch(
    "modules.manage_folders.get_file_path_by_extension",
    return_value="folder_1/folder_2/folder_3/example_ntf_file.ntf",
)
@patch("modules.manage_folders.is_correct_ntf_file", mock_function)
def test_get_ntf_file_and_folder_path(mock_get_file_path_by_extension):
    assert get_ntf_file_and_folder_path("folder_1") == (
        "example_ntf_file.ntf",
        "folder_1/folder_2/folder_3",
    )
    mock_get_file_path_by_extension.assert_called_once_with(
        "folder_1", ".ntf", mock_function
    )


def test_is_correct_ntf_file():
    assert is_correct_ntf_file("example_ntf_file.ntf")
    assert not is_correct_ntf_file("example_not_ntf_file.txt")
    assert not is_correct_ntf_file("example_ntf_file-pan.ntf")
