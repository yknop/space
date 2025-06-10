from datetime import datetime

from bson.objectid import ObjectId
from pymongo.database import Database

from utils.env.get_env import get_env
from utils.logger.write import get_logger

env = get_env()
logger = get_logger()


def insert_image(db: Database, photo_date: datetime, image_name: str, satellite: str) -> ObjectId:
    collection_name = env.collection_name
    return insert_mongodb(
        db,
        collection_name,
        {
            "image_name": image_name,
            "photo_time": photo_date,
            "test_start_time": datetime.now(),
            "satellite_name": satellite,
        },
    )


def insert_mongodb(db: Database, collection_name: str, insert_object: dict) -> ObjectId:
    try:
        inserted_id = db[collection_name].insert_one(insert_object).inserted_id
        return inserted_id
    except Exception as error:
        error_log = "An error occurred when inserting object to db"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
