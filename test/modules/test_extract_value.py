import json
import pytest

from modules.extract_value import get_value_by_keys, get_company_by_folder_name


def test_get_value_by_keys(tmp_path):
    file_path = tmp_path / "test.json"
    data = {"key1": {"key1.1": "value1"}, "key2": "value2"}
    file_path.write_text(json.dumps(data))

    assert get_value_by_keys(file_path, ["key1", "key1.1"]) == "value1"
    assert get_value_by_keys(file_path, ["key2"]) == "value2"
    with pytest.raises(KeyError, match="Key not found"):
        get_value_by_keys(file_path, ["missing_key"])


def test_get_value_by_keys_file_not_found(tmp_path):
    file_path = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError, match="File not found"):
        get_value_by_keys(file_path, ["any_key"])


def test_get_value_by_keys_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{invalid json")
    with pytest.raises(ValueError, match="Invalid JSON file"):
        get_value_by_keys(file_path, ["any_key"])


def test_get_satellite_name_bsg():
    assert get_company_by_folder_name("BSG123_image") == "BlackSky"


def test_get_satellite_name_ssc():
    assert get_company_by_folder_name("123_ssc8_image") == "planet"
