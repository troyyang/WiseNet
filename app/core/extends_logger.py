import logging
import os
from functools import lru_cache
from logging.handlers import RotatingFileHandler

log_dir_path = 'data/logs'

logger = logging.getLogger('WiseNet')  # Create a dedicated logger instance

@lru_cache()
def log_init(log_level=logging.DEBUG):  # Allow configuration of logging level
    """
    Initializes the logging system.

    Args:
        log_level (int): The logging level. Defaults to logging.DEBUG.
    """
    # Create log directory if it does not exist
    if not os.path.isdir(log_dir_path):
        try:
            os.makedirs(log_dir_path)
        except Exception as e:
            print(f'Error creating log directory: {e}')  # Basic error handling

    # Set logger level
    logger.setLevel(log_level)

    # add console handler
    console_handler = logging.StreamHandler()
    # add file handler, used to output logs to file
    file_handler = RotatingFileHandler(filename=os.path.join(log_dir_path, 'wisenet-data.log'),
                                       maxBytes=50 * 1024 * 1024,
                                       backupCount=9,
                                       encoding='UTF-8')

    # set formatter
    formatter = logging.Formatter(
        '[%(asctime)s] -- %(levelname)s - [%(thread)d][%(threadName)s] -- %(filename)s[line:%(lineno)d] %(name)s : %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # add handler to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("logger initialized")

log_init()
