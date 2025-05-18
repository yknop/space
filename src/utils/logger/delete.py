import datetime
import os
import re


def delete_old_logs_files() -> None:
    today = datetime.date.today()
    days_ago = today - datetime.timedelta(int(os.getenv("DAYS_TO_DELETE_LOG")))
    log_pattern = re.compile(r"^[^.]+\.log(\.\d+)?$")

    for file_name in os.listdir(os.getenv("LOGS_PATH")):
        try:
            if log_pattern.match(file_name):
                remove_log_file(days_ago, file_name)
        except ValueError:
            continue


def remove_log_file(deletion_date: datetime.date, file_name: str) -> None:
    file_date_str = file_name.split(".")[0]
    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
    if file_date == deletion_date:
        file_path = os.path.join(os.getenv("LOGS_PATH"), file_name)
        os.remove(file_path)
