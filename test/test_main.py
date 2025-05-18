import pytest
from unittest.mock import patch, call

from main import (
    main,
    check_image,
    get_image_data,
    insert_image_to_mongo,
    send_to_check_disruptions,
)


@patch("main.connect", return_value="db")
@patch("main.os.getenv", return_value="images_path")
@patch(
    "main.os.listdir",
    return_value=[
        "image_1_example",
        "image_2_example",
        "image_3_example",
    ],
)
@patch("main.check_image")
@patch("main.disconnect")
def test_main(
    mock_disconnect, mock_check_image, mock_listdir, mock_getenv, mock_connect
):
    main()
    mock_connect.assert_called_once_with()
    mock_getenv.assert_called_once_with("IMAGES_PATH")
    mock_listdir.assert_called_once_with("images_path")
    assert mock_check_image.call_count == 3
    mock_check_image.assert_has_calls(
        [
            call("db", "images_path", "image_1_example"),
            call("db", "images_path", "image_2_example"),
            call("db", "images_path", "image_3_example"),
        ]
    )
    mock_disconnect.assert_called_once_with()


@patch("main.connect", side_effect=Exception(""))
@patch("main.os.getenv")
@patch("main.os.listdir")
@patch("main.check_image")
@patch("main.disconnect")
def test_main_when_connect_raise_exception(
    mock_disconnect, mock_check_image, mock_listdir, mock_getenv, mock_connect
):
    main()
    mock_connect.assert_called_once_with()
    mock_getenv.assert_not_called()
    mock_listdir.assert_not_called()
    mock_check_image.assert_not_called()
    mock_disconnect.assert_not_called()


@patch(
    "main.get_image_data",
    return_value=(
        "json_file_path",
        "tiff_file_name",
        "image_path",
        "satellite_name",
        {"date_location": "01/01/2025", "image_shape": "parallelogram"},
    ),
)
@patch("main.insert_image_to_mongo", return_value="mongo_image_id")
@patch("main.send_to_check_disruptions")
@patch("main.add_end_date_value")
def test_check_image(
    mock_add_end_date_value,
    mock_send_to_check_disruptions,
    mock_insert_image_to_mongo,
    mock_get_image_data,
):
    check_image("db", "images_path", "image_folder")
    mock_get_image_data.assert_called_once_with("images_path", "image_folder")
    mock_insert_image_to_mongo.assert_called_once_with(
        "db", "tiff_file_name", "json_file_path", "01/01/2025", "satellite_name"
    )
    mock_send_to_check_disruptions.assert_called_once_with(
        "db",
        "image_path",
        "mongo_image_id",
        "satellite_name",
        "json_file_path",
        "parallelogram",
    )
    mock_add_end_date_value.assert_called_once_with("db", "mongo_image_id")


@patch(
    "main.get_image_data",
    return_value=(
        "json_file_path",
        "tiff_file_name",
        "image_path",
        "satellite_name",
        {"date_location": "01/01/2025", "image_shape": "parallelogram"},
    ),
)
@patch(
    "main.insert_image_to_mongo",
    side_effect=Exception("An error occured when insert object to db"),
)
@patch("main.send_to_check_disruptions")
@patch("main.add_end_date_value")
def test_check_image_exception_in_insert_image(
    mock_add_end_date_value,
    mock_send_to_check_disruptions,
    mock_insert_image_to_mongo,
    mock_get_image_data,
):
    check_image("db", "images_path", "image_folder")
    mock_get_image_data.assert_called_once_with("images_path", "image_folder")
    mock_insert_image_to_mongo.assert_called_once_with(
        "db", "tiff_file_name", "json_file_path", "01/01/2025", "satellite_name"
    )
    mock_send_to_check_disruptions.assert_not_called()
    mock_add_end_date_value.assert_not_called()


@patch("main.get_metadata_json_file", return_value="example_image_metadata.json")
@patch("main.get_company_by_folder_name", return_value="satellite_name")
@patch(
    "main.get_image_file",
    return_value=("example_image.tif", "images_path/image_folder/example_image.tif"),
)
@patch(
    "main.get_satellite_details",
    return_value={
        "name": "BlackSky",
        "image_shape": "parallelogram",
        "sensors": 0,
        "date_location": ["acquisitionDate"],
    },
)
@patch("main.os.path.splitext", return_value=("example_image", "tif"))
def test_get_image_data(
    mock_splitext,
    mock_get_satellite_details,
    mock_get_image_file,
    mock_get_company_by_folder_name,
    mock_get_metadata_json_file,
):
    assert get_image_data("images_path", "image_folder") == (
        "example_image_metadata.json",
        "example_image",
        "images_path/image_folder/example_image.tif",
        "satellite_name",
        {
            "name": "BlackSky",
            "image_shape": "parallelogram",
            "sensors": 0,
            "date_location": ["acquisitionDate"],
        },
    )
    mock_get_metadata_json_file.assert_called_once_with("images_path/image_folder")
    mock_get_company_by_folder_name.assert_called_once_with("image_folder")
    mock_get_image_file.assert_called_once_with(
        "images_path/image_folder", "satellite_name"
    )
    mock_get_satellite_details.assert_called_once_with("satellite_name")
    mock_splitext.assert_called_once_with("example_image.tif")


@patch("main.insert_image", return_value="return from insert image")
@patch("main.get_value_by_keys", return_value="return from get_value_by_keys")
def test_insert_image_to_mongo(mock_get_value_by_keys, mock_insert_image):
    assert (
        insert_image_to_mongo(
            "db",
            "image_name_example",
            "json_file_path",
            ["key1", "key1.1"],
            "satellite_name",
        )
        == "return from insert image"
    )
    mock_get_value_by_keys.assert_called_once_with("json_file_path", ["key1", "key1.1"])
    mock_insert_image.assert_called_once_with(
        "db", "return from get_value_by_keys", "image_name_example", "satellite_name"
    )


@patch("main.insert_image", side_effect=Exception("raise exception from insert image"))
@patch("main.get_value_by_keys", return_value="return from get_value_by_keys")
def test_insert_image_to_mongo_when_insert_image_raise_exception(
    mock_get_value_by_keys, mock_insert_image
):
    with pytest.raises(Exception, match="raise exception from insert image"):
        insert_image_to_mongo(
            "db",
            "image_name_example",
            "json_file_path",
            ["key1", "key1.1"],
            "satellite_name",
        )
    mock_get_value_by_keys.assert_called_once_with("json_file_path", ["key1", "key1.1"])
    mock_insert_image.assert_called_once_with(
        "db", "return from get_value_by_keys", "image_name_example", "satellite_name"
    )


@patch("main.insert_image", return_value="return from insert image")
@patch("main.get_value_by_keys", side_effect=KeyError("Key not found"))
def test_insert_image_to_mongo_when_get_value_by_keys_raise_exception(
    mock_get_value_by_keys, mock_insert_image
):
    assert (
        insert_image_to_mongo(
            "db",
            "image_name_example",
            "json_file_path",
            ["key1", "key1.1"],
            "satellite_name",
        )
        == "return from insert image"
    )
    mock_get_value_by_keys.assert_called_once_with("json_file_path", ["key1", "key1.1"])
    mock_insert_image.assert_called_once_with(
        "db", None, "image_name_example", "satellite_name"
    )


@patch(
    "main.create_background_image", return_value="return from create_background_image"
)
@patch("main.blur_disruption", side_effect=Exception(""))
@patch("main.smear_disruption")
@patch("main.saturation_disruption")
@patch("main.cutting_disruption")
def test_send_to_check_disruptions(
    mock_cutting_disruption,
    mock_saturation_disruption,
    mock_smear_disruption,
    mock_blur_disruption,
    mock_create_background_image,
):
    send_to_check_disruptions(
        "db",
        "image_path_example",
        "mongo_image_id_example",
        "satellite_name_example",
        "json_file_path",
        "image_shape",
    )
    mock_create_background_image.assert_called_once_with("image_path_example")
    mock_blur_disruption.assert_called_once_with(
        "db",
        "image_path_example",
        "mongo_image_id_example",
        "satellite_name_example",
        "json_file_path",
        "image_shape",
        background_image="return from create_background_image",
    )
    mock_smear_disruption.assert_called_once_with(
        "db",
        "image_path_example",
        "mongo_image_id_example",
        "satellite_name_example",
        "json_file_path",
        "image_shape",
        background_image="return from create_background_image",
    )
    mock_saturation_disruption.assert_called_once_with(
        "db",
        "image_path_example",
        "mongo_image_id_example",
        "satellite_name_example",
        "json_file_path",
        "image_shape",
        background_image="return from create_background_image",
    )
    mock_cutting_disruption.assert_called_once_with(
        "db",
        "image_path_example",
        "mongo_image_id_example",
        "satellite_name_example",
        "json_file_path",
        "image_shape",
        background_image="return from create_background_image",
    )
