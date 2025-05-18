import os
from datetime import datetime
from pymongo.database import Database
from bson.objectid import ObjectId


def insert_image(
    db: Database, photo_date: datetime, image_name: str, satellite: str
) -> ObjectId:
    collection_name = os.getenv("IMAGES_COLLECTION_NAME")
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
        raise Exception(f"An error occurred when inserting object to db: {error}")
