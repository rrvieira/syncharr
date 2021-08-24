from . import app
from flask import request, send_file, g
from http import HTTPStatus
import config

from .db import get_db
from . import LOGGER, WORKER_THREAD
from syncharrd.sync_request_validator import is_valid_add_sync_request


@app.route("/sync-request")
def add_sync_request():
    sub_file_path = request.args.get('sub')
    media_file_path = request.args.get('media')
    synched_sub_file_path = request.args.get('synchedSub')

    LOGGER.info("New sync request | sub='{sub}' media='{media}' synchedSub='{synchedSub}'"
                .format(sub=sub_file_path, media=media_file_path, synchedSub=synched_sub_file_path))

    is_valid_request, http_status_code, message = is_valid_add_sync_request(sub_file_path,
                                                                            media_file_path,
                                                                            synched_sub_file_path)

    if is_valid_request:
        return __accept_sync_request(get_db(), sub_file_path, media_file_path, synched_sub_file_path)
    else:
        LOGGER.error(message)
        return http_status_code, message


@app.route("/sync-request/log")
def get_log():
    return send_file(config.CONFIG.log_path)


def __accept_sync_request(pending_sync_db, sub_file_path, media_file_path, synched_sub_file_path):
    pending_sync_db.insert_sync_request(sub_file_path, media_file_path, synched_sub_file_path)
    LOGGER.info("Accepted sync request")
    WORKER_THREAD.notify()
    return "", HTTPStatus.NO_CONTENT

