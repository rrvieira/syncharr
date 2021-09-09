import re
import subprocess
from .base_sync_command import BaseSyncCommand, SyncResult


class SubsyncCommand(BaseSyncCommand):

    @staticmethod
    def name():
        return "sc0ty/subsync"

    def __init__(self, subsync_bin_path, logger, window_size_setting, verbose_setting):
        BaseSyncCommand.__init__(self, subsync_bin_path, logger, window_size_setting, verbose_setting)

    def _execute_sync(self, sync_request):

        process = subprocess.Popen([
            self.bin_path,
            '--cli',
            'sync',
            '--sub',
            '{}'.format(sync_request.sub_path),
            '--ref',
            '{}'.format(sync_request.media_path),
            '--out',
            '{}'.format(sync_request.synched_sub_path),
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

        return SyncResult(self.name(), return_code, ref_type, ref_lang)


class InfoMatcher:
    def __init__(self, regex):
        self.regex = regex

    def find(self, text):
        matches = re.findall(self.regex, text)
        if len(matches) == 1:
            return matches[0]

        return None
