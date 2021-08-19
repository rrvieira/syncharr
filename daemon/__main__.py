from . import db
import config
import time
import subprocess
import logging
import signal
import sys

logging.basicConfig(filename=config.syncharrConfig.logPath, 
					format='%(asctime)s %(message)s') 
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

pSyncDB = db.PendingSyncDB(config.syncharrConfig.databasePath)

def main():
    logger.info("--- Starting up ---") 
    while True:
        logger.info("Retrieving pending sync requests...") 
        syncRequests = pSyncDB.get_peding_syncs()
        logger.info("Pending sync requests: {}".format(len(syncRequests)))

        for request in syncRequests:
            launch(request)
            logger.info("Removing finished sync request with id: {}".format(request.id))
            pSyncDB.delete_peding_sync(request.id)

        time.sleep(config.syncharrConfig.databasePollingTime)
    return

def launch(syncRequest):
    logger.info("Going to sync request | id='{id}' subPath='{subPath}' mediaPath='{mediaPath}' synchedSubPath='{synchedSubPath}'".format(id=syncRequest.id, subPath=syncRequest.subPath, mediaPath=syncRequest.mediaPath, synchedSubPath=syncRequest.synchedSubPath))
    process = subprocess.Popen([
        config.syncharrConfig.subsyncBinPath, 
        '--cli',
        'sync',
        '--sub',
        '{}'.format(syncRequest.subPath),
        '--ref',
        '{}'.format(syncRequest.mediaPath),
        '--out',
        '{}'.format(syncRequest.synchedSubPath),
        '--overwrite',
        '--window-size={}'.format(str(120)),
        '--verbose={}'.format(str(3))
        ],
        stdout=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        logger.info("\t{}".format(output.strip()))
        return_code = process.poll()
        if return_code is not None:
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines():
                logger.info("\t{}".format(output.strip()))
            break

    logger.info("Sync finished. Return code: {}".format(return_code))
    return return_code

def stop(_signo, _stack_frame):
    pSyncDB.close_db()
    logger.info("Interrupted. Stopped.") 
    sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        stop(signal.SIGINT,0)
    
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)