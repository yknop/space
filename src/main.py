import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

from azure.storage.blob import BlobServiceClient

from db_connections.connection import connect, disconnect
from utils.azure.connect_azure import connect_azure
from utils.azure.extract_blob import extract_blob
from utils.env.get_env import get_env
from utils.images.manage_images import check_image
from utils.logger.write import get_logger

env = get_env()
logger = get_logger()


def execute_check_image(blob_name: str) -> str:
    try:
        db = connect()
        blob_client = connect_azure(blob_name)
        path = extract_blob(blob_client, blob_name)
        check_image(db, f"{path}")
        disconnect()
        shutil.rmtree(os.path.dirname(path))

        logger.info(f"{blob_name} processed successfully.")
    except Exception:
        logger.info(f"{blob_name} failed:\n{traceback.format_exc()}")


def main() -> None:
    try:
        logger.info("🚀 Starting parallel blob processing........................................................")
        # num_workers = env.num_workers
        # blob_service_client = BlobServiceClient.from_connection_string(env.azure_connection_string)
        # container_client = blob_service_client.get_container_client(env.azure_container_name)
        # blob_names = [blob.name for blob in container_client.list_blobs()]

        # with PoolExecutor(max_workers=num_workers) as executor:
        #     [executor.submit(execute_check_image, blob_name) for blob_name in blob_names]

        # logger.info("Finished processing all blobs.")
    except Exception:
        logger.error("Fatal error during blob batch processing.", exc_info=True)
        raise


if __name__ == "__main__":
    main()
