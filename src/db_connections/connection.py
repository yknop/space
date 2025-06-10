from pymongo import MongoClient
from pymongo.database import Database

from utils.env.get_env import get_env
from utils.logger.write import get_logger

env = get_env()
logger = get_logger()


def mongo_client() -> MongoClient:
    if not env.mongo_uri:
        error_log = "Environment variable MONGO_URI is not set"
        logger.error(error_log, exc_info=True)
        raise ValueError(error_log)
    try:
        client = MongoClient(env.mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info("Connection to MongoDB was successful.")
        return client
    except Exception as error:
        error_log = "The connection to MongoDB failed."
        logger.error(error_log, exc_info=True)
        raise RuntimeError(error_log) from error


def connect() -> Database:
    try:
        client = mongo_client()
        mongo_db = env.mongo_database
        db = client[mongo_db]
        return db
    except Exception as error:
        error_log = "An error occurred during database connection"
        logger.error(error_log, exc_info=True)
        raise Exception(error_log) from error


def disconnect() -> None:
    try:
        client = mongo_client()
        client.close()
    except Exception:
        return
