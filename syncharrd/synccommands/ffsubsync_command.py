import subprocess
from .base_sync_command import BaseSyncCommand, SyncResult


class FFSubsyncCommand(BaseSyncCommand):
    @staticmethod
    def name():
        return "smacke/ffsubsync"

    def __init__(self, ffsubsync_bin_path, logger, window_size_setting, verbose_setting):
        BaseSyncCommand.__init__(self, ffsubsync_bin_path, logger, window_size_setting, verbose_setting)

    def _execute_sync(self, sync_request):
        process = subprocess.Popen([
            self.bin_path,
            '{}'.format(sync_request.media_path),
            '-i',
            '{}'.format(sync_request.sub_path),
            '-o',
            '{}'.format(sync_request.synched_sub_path),
            '--max-offset-seconds={}'.format(str(self.window_size_setting))],
            stderr=subprocess.PIPE, universal_newlines=True)

        ref_used_for_sync_finder = RefUsedForSyncFinder()

        while True:
            output = process.stderr.readline()

            self.logger.info("\t{}".format(output.strip()))
            ref_used_for_sync_finder.update(output)

            return_code = process.poll()

            if return_code is not None:
                for output in process.stderr.readlines():
                    self.logger.info("\t{}".format(output.strip()))
                    ref_used_for_sync_finder.update(output)
                break

        if ref_used_for_sync_finder.has_error:
            return_code = -1

        return SyncResult(self.name(), return_code,
                          ref_used_for_sync_finder.ref_type(), ref_used_for_sync_finder.ref_lang())


class RefUsedForSyncFinder:
    __NO_SUBTITLE_STREAM_MESSAGE = "Video file appears to lack subtitle stream"
    __ERROR_MESSAGE = "] ERROR "

    def __init__(self):
        self.is_ref_type_audio = False
        self.has_error = False

    def ref_type(self):
        if self.is_ref_type_audio:
            return "audio"
        else:
            return "subtitle/text"

    @staticmethod
    def ref_lang():
        return None

    def update(self, text):

        if self.is_ref_type_audio:
            pass

        if self.__NO_SUBTITLE_STREAM_MESSAGE in text:
            self.is_ref_type_audio = True

        if self.__ERROR_MESSAGE in text:
            self.has_error = True
