import sqlite3
import config

class PendingSyncRequest:
    def __init__(self, id, subPath, mediaPath, synchedSubPath):
        self.id = id
        self.subPath = subPath
        self.mediaPath = mediaPath
        self.synchedSubPath = synchedSubPath

class PendingSyncDB:
    def __init__(self, databasePath):
        self.db = None
        self.databasePath = databasePath
        self.init_db()
    
    def delete_peding_sync(self, id):
        self.init_db()
        self.db.execute(
                    "DELETE FROM pending_synch_subs WHERE id=?",
                    (id,),
        )
        self.db.commit()

    def get_peding_syncs(self):
        self.init_db()
        cursor = self.db.execute("SELECT * FROM pending_synch_subs")
        rows = cursor.fetchall()
        return [PendingSyncRequest(*request) for request in rows]

    def init_db(self):
        if self.db is None:
            dbSchema = open(config.syncharrConfig.databaseSchema, 'r')
            createDbSchemaScript = dbSchema.read()
            
            db = sqlite3.connect(self.databasePath)
            db.executescript(createDbSchemaScript)
            db.commit()
            print('Database initialized.')
            
            self.db = db
    
    def close_db(self):
        if self.db is not None:
            self.db.close()
            self.db = None