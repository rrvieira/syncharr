from os import path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

from config import CONFIG
from . import LOGGER, SYNC_WORKER_THREAD_EVENT
from .db import PendingSyncDB


class HttpRequestHandler(BaseHTTPRequestHandler):
    __PROTOCOL_VERSION = "HTTP/1.1"
    __SYNC_REQUEST_PATH = "/sync-request?"

    __pending_sync_db = PendingSyncDB(CONFIG.database_path, CONFIG.database_schema)

    def do_GET(self):
        LOGGER.debug("HTTP get request received for path: {}".format(self.path))

        if self.path.startswith(self.__SYNC_REQUEST_PATH):
            params_str = self.path[len(self.__SYNC_REQUEST_PATH):]
            params = parse_qs(params_str)

            sub_file_path = params['sub'][0]
            media_file_path = params['media'][0]
            synched_sub_file_path = params['synchedSub'][0]

            LOGGER.info("New sync request | sub='{sub}' media='{media}' synchedSub='{synchedSub}'"
                        .format(sub=sub_file_path, media=media_file_path, synchedSub=synched_sub_file_path))

            if not sub_file_path:
                self.__send_missing_query_param_error("sub")
            elif not media_file_path:
                self.__send_missing_query_param_error("media")
            elif not synched_sub_file_path:
                self.__send_missing_query_param_error("synchedSub")
            elif not path.exists(str(sub_file_path)):
                LOGGER.error("Sub file does not exist: '{}'".format(str(sub_file_path)))
                self.__send_no_content_response(HTTPStatus.BAD_REQUEST)
            elif not path.exists(str(media_file_path)):
                LOGGER.error("Media file does not exist:  '{}'".format(str(media_file_path)))
                self.__send_no_content_response(HTTPStatus.BAD_REQUEST)
            else:
                self.__accept_sync_request(sub_file_path, media_file_path, synched_sub_file_path)
        else:
            self.__send_no_content_response(HTTPStatus.NOT_FOUND)

    def __accept_sync_request(self, sub_file_path, media_file_path, synched_sub_file_path):
        self.__pending_sync_db.insert_sync_request(sub_file_path, media_file_path, synched_sub_file_path)
        LOGGER.info("Accepted sync request")
        SYNC_WORKER_THREAD_EVENT.set()
        self.__send_no_content_response(HTTPStatus.NO_CONTENT)

    def __send_no_content_response(self, http_status):
        self.protocol_version = self.__PROTOCOL_VERSION
        self.send_response(http_status)
        self.end_headers()

    def __send_missing_query_param_error(self, param_name):
        LOGGER.error("Missing query parm: '{}'".format(param_name))
        self.__send_no_content_response(HTTPStatus.BAD_REQUEST)
