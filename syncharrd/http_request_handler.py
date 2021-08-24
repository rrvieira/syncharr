import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from os import path
from urllib.parse import parse_qs

from .db import PendingSyncDB
from .sync_request_validator import is_valid_add_sync_request


def launch_http_server(worker_thread, logger, config):
    httpd = socketserver.TCPServer(('', 6766), http_request_handler(worker_thread, logger, config))
    httpd.serve_forever()


def http_request_handler(worker_thread, logger, config):
    class HttpRequestHandler(BaseHTTPRequestHandler):
        __PROTOCOL_VERSION = "HTTP/1.1"
        __SYNC_REQUEST_PATH = "/sync-request?"

        __pending_sync_db = PendingSyncDB(config.database_path, config.database_schema, logger)

        def do_GET(self):
            logger.debug("HTTP get request received for path: {}".format(self.path))

            if self.path.startswith(self.__SYNC_REQUEST_PATH):
                params_str = self.path[len(self.__SYNC_REQUEST_PATH):]
                params = parse_qs(params_str)

                sub_file_path = params['sub'][0]
                media_file_path = params['media'][0]
                synched_sub_file_path = params['synchedSub'][0]

                logger.info("New sync request | sub='{sub}' media='{media}' synchedSub='{synchedSub}'"
                            .format(sub=sub_file_path, media=media_file_path, synchedSub=synched_sub_file_path))

                is_valid_request, http_status_code, message = is_valid_add_sync_request(sub_file_path,
                                                                                        media_file_path,
                                                                                        synched_sub_file_path)
                if is_valid_request:
                    self.__accept_sync_request(sub_file_path, media_file_path, synched_sub_file_path)
                else:
                    logger.error(message)
                    self.__send_sync_request_error(http_status_code, message)
            else:
                self.__send_no_content_response(HTTPStatus.NOT_FOUND)

        def __accept_sync_request(self, sub_file_path, media_file_path, synched_sub_file_path):
            self.__pending_sync_db.insert_sync_request(sub_file_path, media_file_path, synched_sub_file_path)
            logger.info("Accepted sync request")
            worker_thread.notify()
            self.__send_no_content_response(HTTPStatus.NO_CONTENT)

        def __send_no_content_response(self, http_status):
            self.protocol_version = self.__PROTOCOL_VERSION
            self.send_response(http_status)
            self.end_headers()

        def __send_sync_request_error(self, http_status_code, message):
            logger.error(message)
            self.__send_no_content_response(http_status_code)

    return HttpRequestHandler
