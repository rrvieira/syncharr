import sqlite3
import threading


class PendingSyncRequest:
    def __init__(self, request_id, sub_path, media_path, synched_sub_path):
        self.request_id = request_id
        self.sub_path = sub_path
        self.media_path = media_path
        self.synched_sub_path = synched_sub_path


class PendingSyncDB:
    def __init__(self, database_path, database_schema_path, logger):
        self.db = None
        self.databasePath = database_path
        self.database_schema_path = database_schema_path
        self.logger = logger
        self.init_db()

    def insert_sync_request(self, sub_path, media_path, synched_sub_path):
        self.init_db()
        try:
            self.db.execute(
                "INSERT INTO pending_synch_subs (sub_path, media_path, synched_sub_path) VALUES (?, ?, ?)",
                (sub_path, media_path, synched_sub_path),
            )
            self.db.commit()
            return True
        except self.db.IntegrityError:
            self.logger.error(f"Request for: '{sub_path}' already registered.")
            return False

    def delete_pending_sync(self, request_id):
        self.init_db()
        self.db.execute(
            "DELETE FROM pending_synch_subs WHERE id=?",
            (request_id,),
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
            self.logger.debug("Database connection initialized in thread: {}".format(threading.current_thread().name))

    def close_db(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            self.logger.debug("Database connection closed in thread: {}".format(threading.current_thread().name))
