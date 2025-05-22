import shutil
import os
import zipfile
import tempfile
import re

from utils.logger.write import logger
from utils.images.manage_images import check_image


def extract_and_process_blob(blob_client, blob_name: str, db):
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, os.path.basename(blob_name))
    try:
        try:
            with open(zip_path, "wb") as f:
                download_stream = blob_client.download_blob()
                for chunk in download_stream.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            folder_name = re.sub(r"\.[^.\\/:]+$", "", blob_name)
            check_image(db, f"{tmpdir}/{folder_name}")

        except Exception as error:
            error_log = f"Failed to process blob: {blob_name}"
            logger.error(error_log, exc_info=True)
            raise Exception(error_log) from error
    finally:
        shutil.rmtree(tmpdir)
