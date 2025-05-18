import json
from typing import Any, List, Optional


def get_value_by_keys(json_file_path: str, keys: List[str]) -> Any:
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
        if keys[0] not in data:
            raise KeyError("Key not found")
        value = data[keys[0]]
        for index in range(len(keys) - 1):
            value = value[keys[index + 1]]
        return value
    except FileNotFoundError as error:
        raise FileNotFoundError("File not found") from error
    except Exception as error:
        raise ValueError("Invalid JSON file") from error


def get_company_by_folder_name(folder_name: str) -> Optional[str]:
    if "BSG" in folder_name:
        return "BlackSky"
    elif "ssc" in folder_name:
        return "planet"
    return None
