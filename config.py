import configparser

class SyncharrConfig:
    def __init__(self, databasePath, databaseSchema, databasePollingTime, logPath, subsyncBinPath):
        self.databasePath = databasePath
        self.databaseSchema = databaseSchema
        self.databasePollingTime = int(databasePollingTime)
        self.logPath = logPath
        self.subsyncBinPath = subsyncBinPath

config = configparser.ConfigParser()
config.read('syncharr.ini')

syncharrConfig = SyncharrConfig(    config['DEFAULT']['DATABASE'],
                                    config['DEFAULT']['DATABASE_SCHEMA'],
                                    config['DEFAULT']['DB_POLLING_TIME_SECONDS'],
                                    config['DEFAULT']['LOG_PATH'],
                                    config['DEFAULT']['SUBSYNC_BIN_PATH'])
