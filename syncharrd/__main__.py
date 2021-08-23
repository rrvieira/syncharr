import socketserver
import signal
import threading

from . import LOGGER, SYNC_WORKER_THREAD_EVENT
from .http_request_handler import HttpRequestHandler
from .sync_worker_thread import sync_worker_thread


def main():
    LOGGER.info("--- App launched ---")
    launch_worker_thread()
    launch_http_server()


def launch_http_server():
    httpd = socketserver.TCPServer(('', 6766), HttpRequestHandler)
    # httpd = HTTPServer(server_address, HttpRequestHandler)
    httpd.serve_forever()


def launch_worker_thread():
    worker = threading.Thread(target=sync_worker_thread, args=(SYNC_WORKER_THREAD_EVENT,), daemon=True)
    worker.start()


if __name__ == '__main__':
    main()
