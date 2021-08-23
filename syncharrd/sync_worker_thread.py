import subprocess

from config import CONFIG
from . import LOGGER
from .db import PendingSyncDB
import os


def sync_worker_thread(e):
    LOGGER.info("Sync work thread is running.")

    pending_sync_db = PendingSyncDB(CONFIG.database_path, CONFIG.database_schema)

    while True:
        LOGGER.info("Retrieving pending sync requests...")
        sync_requests = pending_sync_db.get_pending_syncs()

        if len(sync_requests) > 0:
            LOGGER.info("New {} sync requests".format(len(sync_requests)))
        else:
            LOGGER.info("No pending sync requests")

        for request in sync_requests:
            launch(request)
            LOGGER.info("Removing sync request with id: {}".format(request.id))
            pending_sync_db.delete_pending_sync(request.id)

        LOGGER.info("Waiting for new sync requests...")
        e.wait()
        e.clear()


def launch(sync_request):
    LOGGER.info("Going to sync request | id='{id}' subPath='{subPath}' mediaPath='{mediaPath}'"
                " synchedSubPath='{synchedSubPath}'".
                format(id=sync_request.id, subPath=sync_request.subPath,
                       mediaPath=sync_request.mediaPath, synchedSubPath=sync_request.synchedSubPath))

    my_env = os.environ.copy()
    my_env["PYTHONUNBUFFERED"] = "0"

    process = subprocess.Popen([
        CONFIG.subsync_bin_path,
        '--cli',
        'sync',
        '--sub',
        '{}'.format(sync_request.subPath),
        '--ref',
        '{}'.format(sync_request.mediaPath),
        '--out',
        '{}'.format(sync_request.synchedSubPath),
        '--overwrite',
        '--window-size={}'.format(str(120)),
        '--verbose={}'.format(str(2))],
        stdout=subprocess.PIPE, universal_newlines=True, env=my_env, bufsize=1)

    while True:
        output = process.stdout.readline()
        LOGGER.info("\t{}".format(output.strip()))
        return_code = process.poll()
        if return_code is not None:
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                LOGGER.info("\t{}".format(output.strip()))
            break

    LOGGER.info("Sync finished. Return code: {}".format(return_code))
    return return_code
