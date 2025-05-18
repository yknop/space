from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
import pytest

from db_connections.update_object import (
    update_mongodb,
    add_end_date_value,
    add_disruption,
)


class MockCollection:
    def __init__(self, raise_exception=False):
        self.raise_exception = raise_exception

    def update_one(self, filter, update_object):
        if not self.raise_exception:
            update_object = MagicMock(
                raw_result={
                    "electionId": ObjectId("7fffffff000000000000009e"),
                    "updatedExisting": True,
                    "acknowledged": True,
                }
            )
            return update_object
        else:
            raise Exception("exception in update_object")


@patch("db_connections.update_object.os.getenv", return_value="images")
@patch(
    "db_connections.update_object.datetime", **{"now.return_value": "return from now"}
)
@patch("db_connections.update_object.update_mongodb", return_value=True)
def test_add_end_date_value_with_valid_ObjectId(
    mock_update_mongodb, mock_now, mock_getenv
):
    add_end_date_value("db", "670d1b37253b447a299bf79e")
    mock_getenv.assert_called_once_with("IMAGES_COLLECTION_NAME")
    mock_now.now.assert_called_once_with()
    mock_update_mongodb.assert_called_once_with(
        "db",
        "images",
        {"_id": ObjectId("670d1b37253b447a299bf79e")},
        {"end-date": "return from now"},
    )


@patch("db_connections.update_object.os.getenv", return_value="images")
@patch(
    "db_connections.update_object.datetime", **{"now.return_value": "return from now"}
)
@patch("db_connections.update_object.update_mongodb")
def test_add_end_date_value_with_not_valid_ObjectId(
    mock_update_mongodb, mock_now, mock_getenv
):
    with pytest.raises(Exception) as exception:
        add_end_date_value("db", "670d1b47a299bf79e")
    assert str(exception.value) == "670d1b47a299bf79e is not a valid ObjectId"
    mock_getenv.assert_not_called()
    mock_now.now.assert_not_called()
    mock_update_mongodb.assert_not_called()


def test_update_mongodb():
    collection_name = "example_collection"
    filter = {"_id": "12345"}
    assert (
        update_mongodb(
            {"example_collection": MockCollection()},
            collection_name,
            filter,
            {"content_1_example": "content"},
        )
        is True
    )


@patch("db_connections.update_object.ObjectId", return_value="object_id")
@patch("db_connections.update_object.os.getenv", return_value="images")
@patch("db_connections.update_object.update_mongodb", return_value=True)
def test_add_disruption(mock_update_mongodb, mock_getenv, mock_ObjectId):
    add_disruption("db", "image_id", "blur", "polygon")
    mock_ObjectId.assert_called_once_with("image_id")
    mock_getenv.assert_called_once_with("IMAGES_COLLECTION_NAME")
    mock_update_mongodb.assert_called_once_with(
        "db", "images", {"_id": "object_id"}, {"blur": "polygon"}
    )


@patch("db_connections.update_object.ObjectId", side_effect=Exception(""))
@patch("db_connections.update_object.os.getenv", return_value="images")
@patch("db_connections.update_object.update_mongodb", return_value=True)
def test_add_disruption_when_image_id_not_valid(
    mock_update_mongodb, mock_getenv, mock_ObjectId
):
    with pytest.raises(ValueError) as error:
        add_disruption("db", "image_id", "blur", "polygon")
    assert str(error.value) == "image_id is not a valid ObjectId"
    mock_ObjectId.assert_called_once_with("image_id")
    mock_getenv.assert_not_called()
    mock_update_mongodb.assert_not_called()


@patch("db_connections.update_object.ObjectId", return_value="object_id")
@patch("db_connections.update_object.os.getenv", return_value="images")
@patch(
    "db_connections.update_object.update_mongodb",
    side_effect=Exception("An error occurred during the update operation."),
)
def test_add_disruption_not_succeed_update_mongodb(
    mock_update_mongodb, mock_getenv, mock_ObjectId
):
    with pytest.raises(Exception) as exception:
        add_disruption("db", "image_id", "blur", "polygon")
    assert str(exception.value) == "An error occurred during the update operation."
    mock_ObjectId.assert_called_once_with("image_id")
    mock_getenv.assert_called_once_with("IMAGES_COLLECTION_NAME")
    mock_update_mongodb.assert_called_once_with(
        "db", "images", {"_id": "object_id"}, {"blur": "polygon"}
    )
