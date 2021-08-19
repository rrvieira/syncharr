#!/bin/sh
python setup.py
python -m daemon &
gunicorn --bind 0.0.0.0:6766 webapp.webapp:app