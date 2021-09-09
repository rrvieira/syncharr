from threading import Event, Thread

from .db import PendingSyncDB
from .synccommands.sync_executor import SyncExecutor
from .notification import TelegramNotification


def launch_worker_thread(logger, config, env_user_settings):
    worker_thread = SyncWorkerThread(logger, config, env_user_settings)
    worker_thread.start()
    return worker_thread


class SyncWorkerThread(Thread):
    def __init__(self, logger, config, env_user_settings):
        super().__init__()

        self.name = "SyncWorkerThread"
        self.daemon = True

        self.event = Event()
        self.logger = logger
        self.config = config
        self.env_user_settings = env_user_settings

    def __wait(self):
        self.event.wait()
        self.event.clear()

    def notify(self):
        self.event.set()

    def run(self) -> None:
        self.logger.info("Sync work thread is running.")

        pending_sync_db = PendingSyncDB(self.config.database_path, self.config.database_schema, self.logger)
        sync_command_executor = SyncExecutor(self.config.subsync_bin_path,
                                             self.config.ff_subsync_bin_path,
                                             self.logger,
                                             self.env_user_settings.sync_tools,
                                             self.env_user_settings.sync_window_size_setting,
                                             self.env_user_settings.sync_verbose_setting)
        telegram_notification = TelegramNotification(self.env_user_settings.telegram_user_token,
                                                     self.env_user_settings.telegram_chat_id,
                                                     self.logger)

        while True:
            self.logger.info("Retrieving pending sync requests...")
            sync_requests = pending_sync_db.get_pending_syncs()

            if len(sync_requests) > 0:
                self.logger.info("New {} sync requests".format(len(sync_requests)))
            else:
                self.logger.info("No pending sync requests")

            for request in sync_requests:
                sync_executor_result = sync_command_executor.sync(request)
                telegram_notification.notify(sync_executor_result)

                self.logger.info("Removing sync request with id: {}".format(request.request_id))
                pending_sync_db.delete_pending_sync(request.request_id)

            self.logger.info("Waiting for new sync requests...")
            self.__wait()
