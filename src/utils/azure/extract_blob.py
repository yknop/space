import os
import re
import tempfile
import zipfile

from azure.storage.blob import BlobClient

from utils.logger.write import get_logger

logger = get_logger()


def extract_blob(blob_client: BlobClient, blob_name: str) -> str:
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, os.path.basename(blob_name))
    try:
        with open(zip_path, "wb") as f:
            download_stream = blob_client.download_blob()
            for chunk in download_stream.chunks():
                f.write(chunk)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        folder_name = re.sub(r"\.[^.\\/:]+$", "", blob_name)
        return f"{tmpdir}/{folder_name}"
    except Exception as error:
        error_log = f"Failed to extract blob: {blob_name}"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
