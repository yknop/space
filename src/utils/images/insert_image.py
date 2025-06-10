from typing import List

from bson import ObjectId
from pymongo.database import Database

from db_connections.insert_object import insert_image
from utils.files.extract_value import get_value_by_keys
from utils.logger.write import get_logger

logger = get_logger()


def insert_image_to_mongo(
    db: Database, image_name: str, json_file_path: str, date_keys: List[str], satellite_name: str
) -> ObjectId:
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
