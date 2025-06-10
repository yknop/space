from azure.storage.blob import BlobClient, BlobServiceClient

from utils.env.get_env import get_env
from utils.logger.write import get_logger

env = get_env()
logger = get_logger()


def connect_azure(blob_name: str) -> BlobClient:
    try:
        connection_string = env.azure_connection_string
        container_name = env.azure_container_name
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        return blob_client
    except Exception as error:
        error_log = "Failed to connect azure"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
