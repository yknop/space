import datetime
import os
import re

from utils.env.get_env import get_env

env = get_env()


def delete_old_logs_files() -> None:
    today = datetime.date.today()
    days_ago = today - datetime.timedelta(int(env.days_to_delete_logs))
    log_pattern = re.compile(r"^[^.]+\.log(\.\d+)?$")

    for file_name in os.listdir(env.logs_path):
        try:
            if log_pattern.match(file_name):
                remove_log_file(days_ago, file_name)
        except ValueError:
            continue


def remove_log_file(deletion_date: datetime.date, file_name: str) -> None:
    file_date_str = file_name.split(".")[0]
    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
    if file_date == deletion_date:
        file_path = os.path.join(env.logs_path, file_name)
        os.remove(file_path)
