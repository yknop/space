from datetime import datetime
from typing import Any, Dict

from bson.objectid import ObjectId
from pymongo import errors
from pymongo.database import Database

from utils.env.get_env import get_env
from utils.logger.write import get_logger

env = get_env()
logger = get_logger()


def add_end_date_value(db: Database, image_id: ObjectId) -> None:
    try:
        _id = ObjectId(image_id)
    except Exception as error:
        error_log = f"{image_id} is not a valid ObjectId"
        logger.error(error_log, exc_info=True)
        raise ValueError(error_log) from error
    try:
        collection_name = env.collection_name
        update_mongodb(db, collection_name, {"_id": _id}, {"end-date": datetime.now()})
        logger.info("Success to update the end date")
    except Exception as error:
        error_log = "Failed to add end date"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def update_mongodb(
    db: Database, collection_name: str, filter: Dict[str, Any], object_value: Any
) -> bool:
    try:
        result = db[collection_name].update_one(filter, {"$set": object_value})
        if not result.matched_count:
            raise errors.WriteError("No document matched the filter criteria.")
        logger.info("Mongo update successful")
        return bool(result.modified_count)
    except errors.WriteError as error:
        error_log = "Update operation did not modify any document"
        logger.error(error_log, exc_info=True)
        raise errors.WriteError(error_log) from error
    except errors.PyMongoError as error:
        error_log = "An error occurred during the update operation"
        logger.error(error_log, exc_info=True)
        raise errors.PyMongoError(error_log) from error


def add_disruption(
    db: Database, image_id: ObjectId, disruption_name: str, polygon: bool = True
) -> None:
    try:
        _id = ObjectId(image_id)
    except Exception as error:
        error_log = f"{image_id} is not a valid ObjectId"
        logger.error(error_log, exc_info=True)
        raise ValueError(error_log) from error
    try:
        collection_name = env.collection_name
        update_mongodb(db, collection_name, {"_id": _id}, {disruption_name: polygon})
    except Exception as error:
        error_log = "Failed to add disruptoin"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error
