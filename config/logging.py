import logging
import sys
from types import FrameType
from typing import cast

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logger(debug, loguru_format):
    logging_level = logging.DEBUG if debug else logging.INFO

    django_logger = logging.getLogger("django")
    django_logger.propagate = False

    loggers = (
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.asgi",
    )

    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.propagate = False
        logging_logger.handlers = [InterceptHandler(level=logging_level)]

    logger.configure(
        handlers=[{"sink": sys.stderr, "level": logging_level, "format": loguru_format}],
    )
