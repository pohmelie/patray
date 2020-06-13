import logging
import sys

from loguru import logger

__all__ = (
    "configure_logging",
)

ALLOWED_LOG_LEVELS = {'ERROR', 'INFO', 'DEBUG', 'WARN'}


# https://github.com/Delgan/loguru/issues/78
class InterceptHandler(logging.Handler):

    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens
        # to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def configure_logging(log_level):
    if log_level not in ALLOWED_LOG_LEVELS:
        raise ValueError(f"Invalid LOG_LEVEL {log_level}")
    logger.configure(
        handlers=[
            dict(
                sink=sys.stderr,
                level=log_level,
            ),
        ],
    )
    logging.basicConfig(level=log_level, handlers=[InterceptHandler()])
