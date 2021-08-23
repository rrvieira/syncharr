# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
from flask import request, send_file
from . import db
import config
import os.path

@app.route("/sync-request")
def home():
    subFilePath = request.args.get('sub')
    mediaFilePath = request.args.get('media')
    synchedSubFilePath = request.args.get('synchedSub')

    if not subFilePath:
        return 'sub is required.', 400
    elif not mediaFilePath:
        return 'media is required.', 400
    elif not synchedSubFilePath:
        return 'synchedSub is required.', 400

#    if not os.path.isfile(subFilePath):
#        return "sub file path does not exist", 400
#    elif not os.path.isfile(mediaFilePath):
#        return "media file path does not exist", 400

    db.insert_sync_request(subFilePath, mediaFilePath, synchedSubFilePath)

    return "", 201

@app.route("/sync-request/log")
def get_data():
    return send_file(config.CONFIG.log_path)