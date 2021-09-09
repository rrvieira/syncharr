import re
import abc
from timeit import default_timer as timer
from datetime import timedelta


class BaseSyncCommand:
    def __init__(self, bin_path, logger, window_size_setting, verbose_setting):
        self.bin_path = bin_path
        self.logger = logger
        self.window_size_setting = window_size_setting
        self.verbose_setting = verbose_setting

        self.logger.info("Sync tool initialized: {name} | binPath='{binPath}' windowSize='{windowSize}'"
                         " verbose='{verbose}'".format(name=self.name(),
                                                       binPath=self.bin_path,
                                                       windowSize=self.window_size_setting,
                                                       verbose=self.verbose_setting))

    @staticmethod
    @abc.abstractmethod
    def name():
        pass

    @abc.abstractmethod
    def _execute_sync(self, sync_request):
        pass

    def sync(self, sync_request):
        self.logger.info("[{name}]: going to sync request | id='{id}' subPath='{subPath}' mediaPath='{mediaPath}'"
                         " synchedSubPath='{synchedSubPath}'".format(name=self.name(),
                                                                     id=sync_request.request_id,
                                                                     subPath=sync_request.sub_path,
                                                                     mediaPath=sync_request.media_path,
                                                                     synchedSubPath=sync_request.synched_sub_path))

        start_timer = timer()
        sync_result = self._execute_sync(sync_request)
        end_timer = timer()

        if sync_result.time_consumed is None:
            sync_result.time_consumed = timedelta(seconds=end_timer - start_timer)

        self.logger.info("[{name}]: sync finished in: '{time}'. Ref type: {refType}, Ref lang: {refLang},"
                         " Return code: {returnCode}".format(name=self.name(),
                                                             time=str(sync_result.time_consumed),
                                                             refType=sync_result.ref_type,
                                                             refLang=sync_result.ref_lang,
                                                             returnCode=sync_result.return_code))

        return sync_result


class SyncResult:
    def __init__(self, sync_by_name, return_code, ref_type, ref_lang, time_consumed=None):
        self.sync_by_name = sync_by_name
        self.return_code = return_code
        self.ref_type = ref_type
        self.ref_lang = ref_lang
        self.time_consumed = time_consumed

    def was_success(self):
        return self.return_code == 0

    def reference(self):
        if self.ref_type is None:
            return "n/a"
        elif self.ref_lang is not None:
            return self.ref_type + ", {}".format(self.ref_lang)
        else:
            return self.ref_type
