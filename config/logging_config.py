import logging
import sys
from config.settings import settings


def setup_logging() -> None:
    """Configures the logging system for the project to output to both console and log file."""
    log_level_str = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    handlers = []

    # Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File Handler (Only if LOG_FILE is defined)
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Root Logger Setup
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(log_level)
    for handler in handlers:
        root_logger.addHandler(handler)

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized with level: %s", log_level_str)
    if settings.LOG_FILE:
        logger.info("Logging to file enabled: %s", settings.LOG_FILE)
