import flask
import logging
import sys

from config import CONFIG, ENV_USER_SETTINGS
from syncharrd.sync_worker_thread import launch_worker_thread

logging.basicConfig(filename=CONFIG.log_path, format='%(asctime)s %(message)s')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

# LOGGER.addHandler(logging.StreamHandler(sys.stdout))

WORKER_THREAD = launch_worker_thread(LOGGER, CONFIG, ENV_USER_SETTINGS)

app = flask.Flask(__name__)
