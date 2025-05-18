import os
from datetime import datetime
from pymongo import errors
from bson.objectid import ObjectId


def add_end_date_value(db, image_id):
    try:
        _id = ObjectId(image_id)
    except Exception:
        raise ValueError(f"{image_id} is not a valid ObjectId") from None
    try:
        collection_name = os.getenv("IMAGES_COLLECTION_NAME")
        update_mongodb(db, collection_name, {"_id": _id}, {"end-date": datetime.now()})
    except Exception as error:
        raise error


def update_mongodb(db, collection_name, filter, object_value):
    try:
        result = db[collection_name].update_one(filter, {"$set": object_value})
        if not result.matched_count:
            raise errors.WriteError("No document matched the filter criteria.")
        return bool(result.modified_count)
    except errors.WriteError as error:
        raise errors.WriteError(
            f"Update operation did not modify any document: {error}"
        )
    except errors.PyMongoError as error:
        raise errors.PyMongoError(
            f"An error occurred during the update operation: {error}"
        )


def add_disruption(db, image_id, disruption_name, polygon=True):
    try:
        _id = ObjectId(image_id)
    except Exception:
        raise ValueError(f"{image_id} is not a valid ObjectId") from None
    try:
        collection_name = os.getenv("IMAGES_COLLECTION_NAME")
        update_mongodb(db, collection_name, {"_id": _id}, {disruption_name: polygon})
    except Exception as error:
        raise error
