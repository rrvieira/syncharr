import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import config

def init_app(app):
    app.teardown_appcontext(close_db)

def insert_sync_request(subFilePath, mediaFilePath, synchedSubFilePath):
    db = get_db()
    try:
        db.execute(
                    "INSERT INTO pending_synch_subs (subPath, mediaPath, synchedSubPath) VALUES (?, ?, ?)",
                    (subFilePath, mediaFilePath, synchedSubFilePath),
        )
        db.commit()
        return True
    except db.IntegrityError:
        error = f"Request for: '{subFilePath}' already registered."
        return False

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            config.CONFIG.database_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()