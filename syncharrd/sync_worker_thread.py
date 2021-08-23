import subprocess
from threading import Event, Thread

from .db import PendingSyncDB


def launch_worker_thread(logger, config):
    worker_thread = SyncWorkerThread(logger, config)
    worker_thread.start()
    return worker_thread


class SyncWorkerThread(Thread):
    def __init__(self, logger, config):
        super().__init__()

        self.name = "SyncWorkerThread"
        self.daemon = True

        self.event = Event()
        self.logger = logger
        self.config = config

    def __wait(self):
        self.event.wait()
        self.event.clear()

    def notify(self):
        self.event.set()

    def run(self) -> None:
        self.logger.info("Sync work thread is running.")

        pending_sync_db = PendingSyncDB(self.config.database_path, self.config.database_schema, self.logger)

        while True:
            self.logger.info("Retrieving pending sync requests...")
            sync_requests = pending_sync_db.get_pending_syncs()

            if len(sync_requests) > 0:
                self.logger.info("New {} sync requests".format(len(sync_requests)))
            else:
                self.logger.info("No pending sync requests")

            for request in sync_requests:
                self.launch(request)
                self.logger.info("Removing sync request with id: {}".format(request.request_id))
                pending_sync_db.delete_pending_sync(request.request_id)

            self.logger.info("Waiting for new sync requests...")
            self.__wait()

    def launch(self, sync_request):
        self.logger.info("Going to sync request | id='{id}' subPath='{subPath}' mediaPath='{mediaPath}'"
                         " synchedSubPath='{synchedSubPath}'".
                         format(id=sync_request.request_id, subPath=sync_request.sub_path,
                                mediaPath=sync_request.media_path, synchedSubPath=sync_request.synched_sub_path))

        process = subprocess.Popen([
            self.config.subsync_bin_path,
            '--cli',
            'sync',
            '--sub',
            '{}'.format(sync_request.sub_path),
            '--ref',
            '{}'.format(sync_request.media_path),
            '--out',
            '{}'.format(sync_request.synched_sub_path),
            '--overwrite',
            '--window-size={}'.format(str(120)),
            '--verbose={}'.format(str(2))],
            stdout=subprocess.PIPE, universal_newlines=True)

        while True:
            output = process.stdout.readline()
            self.logger.info("\t{}".format(output.strip()))
            return_code = process.poll()
            if return_code is not None:
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    self.logger.info("\t{}".format(output.strip()))
                break

        self.logger.info("Sync finished. Return code: {}".format(return_code))
        return return_code
