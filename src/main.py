from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

from db_connections.connection import connect, disconnect
from db_connections.insert_object import insert_image
from db_connections.update_object import add_end_date_value
from modules.consts_by_satellite_name import get_satellite_details
from modules.extract_value import get_value_by_keys, get_company_by_folder_name
from modules.blurring.blur_algorithm import blur_disruption
from modules.cutting.cutting_algorithm import cutting_disruption
from modules.manage_folders import get_metadata_json_file
from modules.manage_images import get_image_file, create_background_image
from modules.saturation.saturation_algorithm import saturation_disruption
from modules.smearing.smear_algorithm import smear_disruption
from utils.logger.write import logger

import tempfile
import re
import shutil
import zipfile

load_dotenv()


def main():
    try:
        db = connect()
        AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
        CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        for blob in container_client.list_blobs():
            logger.info(f"📦️ Starting to process ZIP blob: {blob.name}")
            blob_client = container_client.get_blob_client(blob.name)

            tmpdir = tempfile.mkdtemp()

            zip_path = os.path.join(tmpdir, os.path.basename(blob.name))
  
            try:
                with open(zip_path, "wb") as f:
                    f.write(blob_client.download_blob().readall())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)
                folder_name =re.sub(r'\.[^.\\/:]+$', '', blob.name)
                check_image(db, f"{tmpdir}/{folder_name}")
                shutil.rmtree(tmpdir)

            except Exception as e:
                logger.error(f"Failed to process {blob.name}: {e}")     
            disconnect()
    except Exception as e:
        logger.error(f"Failed to process {blob.name}: {e}")   


def check_image(db, root):
    try:
        (
            json_file_path,
            tiff_file_name,
            image_path,
            satellite_name,
            satellite_details,
        ) = get_image_data(root)
        mongo_image_id = insert_image_to_mongo(
            db,
            tiff_file_name,
            json_file_path,
            satellite_details["date_location"],
            satellite_name,
        )
    except Exception:
        return
    send_to_check_disruptions(
        db,
        image_path,
        mongo_image_id,
        satellite_name,
        json_file_path,
        satellite_details["image_shape"],
    )
    add_end_date_value(db, mongo_image_id)


def get_image_data(root):
    try:
        json_file_path = get_metadata_json_file(root)
        a = re.search(r'[^/\\]+$', root).group(0)
        satellite_name = get_company_by_folder_name(re.search(r'[^/\\]+$', root).group(0))
        tiff_file, image_path = get_image_file(
            root, satellite_name
        )
        satellite_details = get_satellite_details(satellite_name)
        tiff_file_name = os.path.splitext(tiff_file)[0]
        return (
            json_file_path,
            tiff_file_name,
            image_path,
            satellite_name,
            satellite_details,
        )
    except Exception as error:
        error_log = "An error occured when write sub image"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def insert_image_to_mongo(db, image_name, json_file_path, date_keys, satellite_name):
    try:
        try:
            date = get_value_by_keys(json_file_path, date_keys)
        except Exception:
            date = None
        return insert_image(db, date, image_name, satellite_name)
    except Exception as error:
        error_log = "Failed to insert image to mongo"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error

def send_to_check_disruptions(
    db, image_path, mongo_image_id, satellite_name, json_file_path, image_shape
):
    background_image = create_background_image(image_path)
    for disruption in [
        blur_disruption,
        smear_disruption,
        saturation_disruption,
        cutting_disruption,
    ]:
        try:
            disruption(
                db,
                image_path,
                mongo_image_id,
                satellite_name,
                json_file_path,
                image_shape,
                background_image=background_image,
            )
        except Exception:
            continue
        
if __name__ == "__main__":
    main()
