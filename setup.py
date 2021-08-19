import sqlite3
import config

with open(config.syncharrConfig.databaseSchema, 'r') as databaseSchema:
    databaseCreateSchemaScript = databaseSchema.read()

db = sqlite3.connect(config.syncharrConfig.databasePath)
db.executescript(databaseCreateSchemaScript)
db.commit()
db.close()

print('Database initialized.')