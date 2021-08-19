import logging
from . import db
import signal
import subprocess
import sys

import config

logging.basicConfig(filename=config.syncharrConfig.logPath, 
					format='%(asctime)s %(message)s') 
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

pSyncDB = db.PendingSyncDB(config.syncharrConfig.databasePath)

def main():
    return

if __name__ == '__main__':
    main()
