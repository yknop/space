import os
from pymongo import MongoClient
from pymongo.database import Database


def mongo_client() -> MongoClient:
    mongo_uri = os.getenv("MONGO_URI")
    return MongoClient(mongo_uri)


def connect() -> Database:
    try:
        client = mongo_client()
        mongo_db = os.getenv("MONGODB_DATABASE")
        db = client[mongo_db]
        return db
    except Exception as error:
        raise Exception(f"An error occurred during database connection: {error}")


def disconnect() -> None:
    try:
        client = mongo_client()
        client.close()
    except Exception:
        return
