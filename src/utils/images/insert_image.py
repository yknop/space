from bson import ObjectId

from utils.logger.write import logger
from utils.files.extract_value import get_value_by_keys
from db_connections.insert_object import insert_image


def insert_image_to_mongo(
    db, image_name, json_file_path, date_keys, satellite_name
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
