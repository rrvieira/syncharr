#!/bin/sh
gunicorn --bind 0.0.0.0:6766 webapp.webapp:app