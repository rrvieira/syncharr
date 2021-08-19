import flask
from . import db

app = flask.Flask(__name__)
db.init_app(app)