from . import LOGGER, CONFIG, app
from flask import g
from syncharrd.db import PendingSyncDB


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_pending_sync_db', None)
    if db is not None:
        db.close_db()


def get_db():
    db = getattr(g, '_pending_sync_db', None)
    if db is None:
        db = g._pending_sync_db = PendingSyncDB(CONFIG.database_path, CONFIG.database_schema, LOGGER)
    return db
