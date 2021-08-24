import re
import subprocess
from timeit import default_timer as timer
from datetime import timedelta


class SubsyncCommand:
    def __init__(self, subsync_bin_path, logger, window_size_setting, verbose_setting, sync_request):
        self.subsync_bin_path = subsync_bin_path
        self.logger = logger
        self.window_size_setting = window_size_setting
        self.verbose_setting = verbose_setting
        self.sync_request = sync_request

        self.logger.info("Subsync command initialized | binPath='{binPath}' windowSize='{windowSize}'"
                         " verbose='{verbose}'".format(binPath=self.subsync_bin_path,
                                                       windowSize=self.window_size_setting,
                                                       verbose=self.verbose_setting))

    def sync(self):
        self.logger.info("Going to sync request | id='{id}' subPath='{subPath}' mediaPath='{mediaPath}'"
                         " synchedSubPath='{synchedSubPath}'".format(id=self.sync_request.request_id,
                                                                     subPath=self.sync_request.sub_path,
                                                                     mediaPath=self.sync_request.media_path,
                                                                     synchedSubPath=self.sync_request.synched_sub_path))

        start_timer = timer()

        process = subprocess.Popen([
            self.subsync_bin_path,
            '--cli',
            'sync',
            '--sub',
            '{}'.format(self.sync_request.sub_path),
            '--ref',
            '{}'.format(self.sync_request.media_path),
            '--out',
            '{}'.format(self.sync_request.synched_sub_path),
            '--overwrite',
            '--window-size={}'.format(str(self.window_size_setting)),
            '--verbose={}'.format(str(self.verbose_setting))],
            stdout=subprocess.PIPE, universal_newlines=True)

        ref_type_matcher = InfoMatcher(r"^\[\+\]\sref:\s.*(?<=type=)(.*?)(?=,)")
        ref_lang_matcher = InfoMatcher(r"^\[\+\]\sref:\s.*(?<=lang=)(.*?)(?=,)")
        ref_type = None
        ref_lang = None

        while True:
            output = process.stdout.readline()

            self.logger.info("\t{}".format(output.strip()))

            if ref_type is None:
                ref_type = ref_type_matcher.find(output)
            if ref_lang is None:
                ref_lang = ref_lang_matcher.find(output)

            return_code = process.poll()

            if return_code is not None:
                for output in process.stdout.readlines():
                    self.logger.info("\t{}".format(output.strip()))

                    if ref_type is None:
                        ref_type = ref_type_matcher.find(output)
                    if ref_lang is None:
                        ref_lang = ref_lang_matcher.find(output)
                break

        end_timer = timer()

        self.logger.info("Sync finished[{time}]. Ref type: {refType}, Ref lang: {refLang},"
                         " Return code: {returnCode}".format(time=str(timedelta(seconds=end_timer - start_timer)),
                                                             refType=ref_type,
                                                             refLang=ref_lang,
                                                             returnCode=return_code))

        return SyncResult(return_code == 0,
                          ref_type, ref_lang, timedelta(seconds=end_timer - start_timer), self.sync_request)


class InfoMatcher:
    def __init__(self, regex):
        self.regex = regex

    def find(self, text):
        matches = re.findall(self.regex, text)
        if len(matches) == 1:
            return matches[0]

        return None


class SyncResult:
    def __init__(self, success, ref_type, ref_lang, time_consumed, sync_request):
        self.success = success
        self.ref_type = ref_type
        self.ref_lang = ref_lang
        self.time_consumed = time_consumed
        self.sync_request = sync_request

    def media_file_path(self):
        return self.sync_request.media_path

    def original_sub_file_path(self):
        return self.sync_request.sub_path

    def sub_language(self):
        regex = r"(?<=\.)(.*?)(?=\.srt$)"
        matches = re.findall(regex, self.sync_request.sub_path)

        if len(matches) == 1:
            return matches[0]

        return None
