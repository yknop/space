from unittest.mock import patch, MagicMock
from db_connections.connection import mongo_client, connect, disconnect


@patch("db_connections.connection.MongoClient")
@patch("db_connections.connection.os.getenv", return_value="mock_uri")
def test_mongo_client(mock_getenv, mock_mongo_client):
    client = mongo_client()
    mock_getenv.assert_called_once_with("MONGO_URI")
    mock_mongo_client.assert_called_once_with("mock_uri")
    assert client == mock_mongo_client.return_value


@patch("db_connections.connection.MongoClient")
@patch("db_connections.connection.os.getenv")
def test_connect(mock_getenv, mock_mongo_client):
    mock_getenv.side_effect = ["mock_uri", "mock_db"]
    mock_db = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db
    db = connect()
    assert db == mock_db
    mock_mongo_client.assert_called_once_with("mock_uri")


@patch("db_connections.connection.MongoClient")
def test_disconnect(mock_mongo_client):
    mock_client_instance = mock_mongo_client.return_value
    disconnect()
    mock_client_instance.close.assert_called_once()


@patch("db_connections.connection.mongo_client")
def test_connect_exception(mock_mongo_client):
    mock_mongo_client.side_effect = Exception("Connection Error")
    try:
        connect()
    except Exception as error:
        assert "An error occurred during database connection" in str(error)


@patch("db_connections.connection.mongo_client")
def test_disconnect_exception(mock_mongo_client):
    mock_mongo_client.side_effect = Exception("Disconnection Error")
    assert disconnect() is None
