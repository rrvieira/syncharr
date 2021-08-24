import logging
import sys

from config import CONFIG, ENV_USER_SETTINGS, ENV_PROJ_SETTINGS
from .http_request_handler import launch_http_server
from .sync_worker_thread import launch_worker_thread


def main():
    logger = setup_logger()
    config = setup_config()

    logger.info("--- App launched ---")

    worker_thread = launch_worker_thread(logger, config, ENV_USER_SETTINGS)
    launch_http_server(worker_thread, logger, config)


def setup_logger():
    logging.basicConfig(filename=CONFIG.log_path, format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if ENV_PROJ_SETTINGS.log_console_enabled:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger


def setup_config():
    return CONFIG


if __name__ == '__main__':
    main()
