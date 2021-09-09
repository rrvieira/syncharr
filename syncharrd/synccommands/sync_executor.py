import re
from .subsync_command import SubsyncCommand
from .ffsubsync_command import FFSubsyncCommand


class SyncExecutor:
    def __init__(self, subsync_bin_path, ffsubsync_bin_path,
                 logger, sync_tools_name_list, window_size_setting, verbose_setting):
        self.subsync_bin_path = subsync_bin_path
        self.ffsubsync_bin_path = ffsubsync_bin_path
        self.logger = logger
        self.window_size_setting = window_size_setting
        self.verbose_setting = verbose_setting

        self.__setup(sync_tools_name_list)

    def __setup(self, sync_tools_name_list):
        self.sync_tools = []
        for tool_name in sync_tools_name_list:
            if tool_name == SubsyncCommand.name():
                self.sync_tools.append(self.__setup_subsync())
            elif tool_name == FFSubsyncCommand.name():
                self.sync_tools.append(self.__setup_ffsubsync())

        if self.sync_tools:
            self.logger.info("Sync tools initialized successfully: '{}'".format(str(self.sync_tools_name_list())))
        else:
            self.sync_tools = [self.__setup_subsync(), self.__setup_ffsubsync()]
            self.logger.warning("Sync tools found problems during initialization. Falling back to default: '{}'"
                                .format(str(self.sync_tools_name_list())))

    def __setup_subsync(self):
        return SubsyncCommand(self.subsync_bin_path, self.logger, self.window_size_setting, self.verbose_setting)

    def __setup_ffsubsync(self):
        return FFSubsyncCommand(self.ffsubsync_bin_path, self.logger, self.window_size_setting, self.verbose_setting)

    def sync_tools_name_list(self):
        return list(map(lambda sync_tool: sync_tool.name(), self.sync_tools))

    def sync(self, sync_request):
        sync_result_list = []
        for sync_tool in self.sync_tools:
            sync_result = sync_tool.sync(sync_request)
            sync_result_list.append(sync_result)
            if sync_result.was_success():
                break
            else:
                message_tpl = "Tool '{}' failed to sync. "
                if len(sync_result_list) < len(self.sync_tools):
                    message_tpl += "Going to try again with the next tool available."
                else:
                    message_tpl += "No more tools left to try the sync."

                self.logger.warning(message_tpl.format(sync_tool.name()))

        return SyncExecutorResult(sync_request, sync_result_list)


class SyncExecutorResult:
    def __init__(self, sync_request, sync_result_list):
        self.sync_result_list = sync_result_list
        self.sync_request = sync_request

    def was_success(self):
        for sync_result in self.sync_result_list:
            if not sync_result.was_success():
                return False
        return True

    def media_file_path(self):
        return self.sync_request.media_path

    def original_sub_file_path(self):
        return self.sync_request.sub_path

    def sub_language(self):
        regex = r"(?<=\.)([^.]+?)(?=\.srt$)"
        matches = re.findall(regex, self.sync_request.sub_path)

        if len(matches) == 1:
            return matches[0]

        return None
