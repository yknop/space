import logging
from datetime import datetime
from dotenv import load_dotenv
from pytz import timezone
from typing import Any

load_dotenv()


class CustomFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: Any = None) -> str:
        tz = timezone("Asia/Jerusalem")
        record.asctime = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return record.asctime

def create_logger(logger_name: str) -> logging.Logger:
    FORMAT = 'time="%(asctime)s" level="%(levelname)s" source="%(module)s.%(funcName)s:%(lineno)d" thread=%(thread)d message="%(message)s"'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = CustomFormatter(fmt=FORMAT)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


logger = create_logger(__name__)
