import shutil
import os
from typing import Callable, Optional, Tuple


def create_folder(folder_name: str) -> None:
    if os.path.isdir(f"./{folder_name}"):
        remove_folder(folder_name)
    os.mkdir(f"./{folder_name}")


def remove_folder(folder_name: str) -> None:
    try:
        shutil.rmtree(folder_name)
    except OSError as error:
        raise error


def remove_file(file_name: str) -> None:
    if os.path.exists(file_name):
        os.remove(file_name)


def polygon_image_path(src_path: str, folder_name: str) -> str:
    file_name = os.path.basename(src_path)
    folder_path = os.path.dirname(src_path)
    parent_folder_path = os.path.dirname(folder_path)
    polygon_image_path = os.path.join(parent_folder_path, folder_name, file_name)
    return polygon_image_path


def get_metadata_json_file(folder_path: str) -> str:
    return get_file_path_by_extension(
        folder_path, "metadata.json", is_metadata_json_file
    )


def is_metadata_json_file(file: str) -> bool:
    return file.endswith("metadata.json")


def get_file_path_by_extension(
    folder_path: str, extension: str, func_is_correct_file: Callable[[str], bool]
) -> str:
    file_path = get_file_recursive(folder_path, func_is_correct_file)
    if file_path:
        return file_path
    raise Exception(f"{extension} file was not found.")


def get_file_recursive(
    folder_path: str, func_is_correct_file: Callable[[str], bool]
) -> Optional[str]:
    file_path = get_file_path(folder_path, func_is_correct_file)
    if file_path:
        return file_path
    return get_file_path_from_sub_folders(folder_path, func_is_correct_file)


def get_file_path(
    folder_path: str, func_is_correct_file: Callable[[str], bool]
) -> Optional[str]:
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and func_is_correct_file(file):
            return file_path
    return None


def get_file_path_from_sub_folders(
    folder_path: str, func_is_correct_file: Callable[[str], bool]
) -> Optional[str]:
    for folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, folder)
        if os.path.isdir(sub_folder_path):
            file_path = get_file_recursive(sub_folder_path, func_is_correct_file)
            if file_path:
                return file_path
    return None


def get_tif_file_and_file_path(folder_path: str) -> Tuple[str, str]:
    file_path = get_file_path_by_extension(folder_path, ".tif", is_tif_file)
    return file_path.split("/")[-1], file_path


def is_tif_file(file: str) -> bool:
    return file.endswith(".tif")


def get_ntf_file_and_folder_path(folder_path: str) -> Tuple[str, str]:
    file_path = get_file_path_by_extension(folder_path, ".ntf", is_correct_ntf_file)
    split_file_path = file_path.split("/")
    file = split_file_path.pop()
    folder_path = "/".join(split_file_path)
    return file, folder_path


def is_correct_ntf_file(file: str) -> bool:
    return file.endswith(".ntf") and not file.endswith("-pan.ntf")
