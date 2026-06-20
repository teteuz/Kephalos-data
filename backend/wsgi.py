"""
Production entry point for gunicorn.
Usage: gunicorn wsgi:app
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config

# Warn about missing optional keys but don't exit
errors = Config.validate()
if errors:
    for err in errors:
        logging.warning('Config warning: %s', err)

app = create_app()
