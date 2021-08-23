import sqlite3
import config

with open(config.CONFIG.database_schema, 'r') as databaseSchema:
    databaseCreateSchemaScript = databaseSchema.read()

db = sqlite3.connect(config.CONFIG.database_path)
db.executescript(databaseCreateSchemaScript)
db.commit()
db.close()

print('Database initialized.')