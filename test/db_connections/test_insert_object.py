from unittest.mock import patch
import pytest

from db_connections.insert_object import insert_image, insert_mongodb


class MockCollection:
    def __init__(self, raise_exception=False):
        self.raise_exception = raise_exception

    def insert_one(self, insert_object):
        if not self.raise_exception:
            insert_object["inserted_id"] = "inserted_id"
            return MockObject(insert_object)
        else:
            raise Exception("exception in insert_one")


class MockObject:
    def __init__(self, object):
        self.inserted_id = object["inserted_id"]


@patch("db_connections.insert_object.os.getenv", return_value="images")
@patch(
    "db_connections.insert_object.datetime", **{"now.return_value": "return from now"}
)
@patch(
    "db_connections.insert_object.insert_mongodb",
    return_value="return from insert_mongodb",
)
def test_insert_image(mock_insert_mongodb, mock_now, mock_getenv):
    assert (
        insert_image("db", "photo_date", "image_1_example", "sattelite_1_example")
        == "return from insert_mongodb"
    )
    mock_getenv.assert_called_once_with("IMAGES_COLLECTION_NAME")
    mock_now.now.assert_called_once_with()
    mock_insert_mongodb.assert_called_once_with(
        "db",
        "images",
        {
            "test_start_time": "return from now",
            "image_name": "image_1_example",
            "satellite_name": "sattelite_1_example",
            "photo_time": "photo_date",
        },
    )


def test_insert_mongodb():
    collection_name = "collection_1_example"
    assert (
        insert_mongodb(
            {"collection_1_example": MockCollection()},
            collection_name,
            {"content_1_example": "content", "content_2_example": "content"},
        )
        == "inserted_id"
    )


def test_insert_mongodb_when_insert_one_raise_exception():
    collection_name = "collection_1_example"
    with pytest.raises(Exception) as exception:
        insert_mongodb(
            {"collection_1_example": MockCollection(True)},
            collection_name,
            {"content_1_example": "content", "content_2_example": "content"},
        )
    assert (
        str(exception.value)
        == "An error occured when insert object to db: exception in insert_one"
    )
