import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

from db_connections.connection import connect, disconnect
from utils.logger.write import logger
from utils.azure.extract_blob import extract_and_process_blob

load_dotenv()


def main():
    try:
        logger.info("Start!!!")
        db = connect()
        AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
        CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
        logger.info(f"AZURE_CONNECTION_STRING {AZURE_CONNECTION_STRING}" )
        logger.info(f"AZURE_CONTAINER_NAME {CONTAINER_NAME}" )
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_CONNECTION_STRING
        )
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            try:
                extract_and_process_blob(blob_client, blob.name, db)

            except Exception as error:
                error_log = f"Failed to process {blob.name}"
                logger.error(error_log, exc_info=True)
                raise Exception(error_log) from error

            disconnect()

    except Exception as error:
        error_log = "Failed to process blob"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


if __name__ == "__main__":
    main()
