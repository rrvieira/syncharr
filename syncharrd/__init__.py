import logging
from config import CONFIG
import sys
import threading

logging.basicConfig(filename=CONFIG.log_path, format='%(asctime)s %(message)s')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

# TODO - remove
LOGGER.addHandler(logging.StreamHandler(sys.stdout))

SYNC_WORKER_THREAD_EVENT = threading.Event()
