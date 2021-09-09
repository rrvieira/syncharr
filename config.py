import configparser
import os
import json
from json.decoder import JSONDecodeError


class SyncharrConfig:
    def __init__(self, database_path, database_schema, log_path, subsync_bin_path, ff_subsync_bin_path):
        self.database_path = database_path
        self.database_schema = database_schema
        self.log_path = log_path
        self.subsync_bin_path = subsync_bin_path
        self.ff_subsync_bin_path = ff_subsync_bin_path


class EnvironmentUserSettings:
    def __init__(self, sync_tools, sync_window_size_setting, sync_verbose_setting, telegram_user_token,
                 telegram_chat_id):
        try:
            self.sync_tools = json.loads(sync_tools)
        except (JSONDecodeError, TypeError):
            self.sync_tools = []
        self.sync_window_size_setting = sync_window_size_setting
        self.sync_verbose_setting = sync_verbose_setting
        self.telegram_user_token = telegram_user_token
        self.telegram_chat_id = telegram_chat_id


class EnvironmentProjSettings:
    def __init__(self, log_console_enabled):
        self.log_console_enabled = log_console_enabled


config_parser = configparser.ConfigParser()
config_parser.read('syncharr.ini')

CONFIG = SyncharrConfig(config_parser['DEFAULT']['DATABASE'],
                        config_parser['DEFAULT']['DATABASE_SCHEMA'],
                        config_parser['DEFAULT']['LOG_PATH'],
                        config_parser['DEFAULT']['SUBSYNC_BIN_PATH'],
                        config_parser['DEFAULT']['FFSUBSYNC_BIN_PATH'])

ENV_USER_SETTINGS = EnvironmentUserSettings(os.environ.get('SYNC_TOOLS'),
                                            os.environ.get('SYNC_WINDOW_SIZE_SETTING', 120),
                                            os.environ.get('SYNC_VERBOSE_SETTING', 2),
                                            os.environ.get('TELEGRAM_USER_TOKEN'),
                                            os.environ.get('TELEGRAM_CHAT_ID'))

ENV_PROJ_SETTINGS = EnvironmentProjSettings(bool(os.environ.get('LOG_CONSOLE_ENABLED', False)))
