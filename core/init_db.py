"""
Initializes the database with initial data.
"""

from core.app import create_app
from core.db import db, load_data

app = create_app()

with app.app_context():
    db.create_all()
    load_data()
