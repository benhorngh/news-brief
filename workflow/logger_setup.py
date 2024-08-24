import json
import logging
import os
from logging.handlers import RotatingFileHandler

original_makeRecord = logging.Logger.makeRecord

dummy = logging.LogRecord("dummy", 0, "dummy", 0, None, None, None, None, None)
reserved_keys = list(dummy.__dict__.keys()) + ["message", "asctime"]


class DynamicExtraFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        extra = {k: v for k, v in record.__dict__.items() if k not in reserved_keys}
        if extra:
            result += " " + json.dumps(extra)

        return result


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = DynamicExtraFormatter(
        "%(asctime)s %(name)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def add_file_logger(logger, formatter):
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/logs.log", maxBytes=1 * 1024 * 1024, backupCount=1
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
