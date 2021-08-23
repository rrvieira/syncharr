import configparser


class SyncharrConfig:
    def __init__(self, database_path, database_schema, log_path, subsync_bin_path):
        self.database_path = database_path
        self.database_schema = database_schema
        self.log_path = log_path
        self.subsync_bin_path = subsync_bin_path


config_parser = configparser.ConfigParser()
config_parser.read('syncharr.ini')

CONFIG = SyncharrConfig(config_parser['DEFAULT']['DATABASE'],
                        config_parser['DEFAULT']['DATABASE_SCHEMA'],
                        config_parser['DEFAULT']['LOG_PATH'],
                        config_parser['DEFAULT']['SUBSYNC_BIN_PATH'])
