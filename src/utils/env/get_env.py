import os
from dataclasses import dataclass


@dataclass
class EnvVars:
    azure_connection_string: str
    azure_container_name: str
    collection_name: str
    days_to_delete_logs: str
    logs_path: str
    mongo_database: str
    mongo_uri: str
    num_workers: int


def get_env() -> EnvVars:
    return EnvVars(
        azure_connection_string=os.getenv("AZURE_CONNECTION_STRING"),
        azure_container_name=os.getenv("AZURE_CONTAINER_NAME"),
        collection_name=os.getenv("IMAGES_COLLECTION_NAME"),
        days_to_delete_logs=int(os.getenv("DAYS_TO_DELETE_LOG")),
        logs_path=os.getenv("LOGS_PATH"),
        mongo_database=os.getenv("MONGODB_DATABASE"),
        mongo_uri=os.getenv("MONGO_URI"),
        num_workers=int(os.getenv("NUM_WORKERS", os.cpu_count() * 3 // 4)),
    )
