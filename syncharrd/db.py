import sqlite3
import threading

from config import CONFIG
from . import LOGGER


class PendingSyncRequest:
    def __init__(self, id, subPath, mediaPath, synchedSubPath):
        self.id = id
        self.subPath = subPath
        self.mediaPath = mediaPath
        self.synchedSubPath = synchedSubPath


class PendingSyncDB:
    def __init__(self, database_path, database_schema_path):
        self.db = None
        self.databasePath = database_path
        self.database_schema_path = database_schema_path
        self.init_db()

    def insert_sync_request(self, subPath, mediaPath, synchedSubPath):
        self.init_db()
        try:
            self.db.execute(
                "INSERT INTO pending_synch_subs (subPath, mediaPath, synchedSubPath) VALUES (?, ?, ?)",
                (subPath, mediaPath, synchedSubPath),
            )
            self.db.commit()
            return True
        except self.db.IntegrityError:
            LOGGER.error(f"Request for: '{subPath}' already registered.")
            return False

    def delete_pending_sync(self, id):
        self.init_db()
        self.db.execute(
            "DELETE FROM pending_synch_subs WHERE id=?",
            (id,),
        )
        self.db.commit()

    def get_pending_syncs(self):
        self.init_db()
        cursor = self.db.execute("SELECT * FROM pending_synch_subs")
        rows = cursor.fetchall()
        return [PendingSyncRequest(*request) for request in rows]

    def init_db(self):
        if self.db is None:
            db_schema = open(self.database_schema_path, 'r')
            create_db_schema_script = db_schema.read()

            db = sqlite3.connect(self.databasePath)
            db.executescript(create_db_schema_script)
            db.commit()

            self.db = db
            LOGGER.debug("Database connection initialized in thread: {}".format(threading.get_ident()))

    def close_db(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            LOGGER.debug("Database connection closed in thread: {}".format(threading.get_ident()))
