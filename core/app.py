"""
This module contains the Flask application factory and its configurations.
"""

import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from dotenv import load_dotenv

from core.db import db
from core.routes import bp, cache


load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def create_app(test_config=None):
    """
    Create and configure the Flask application.

    :param test_config: Optional test configuration
    :return: Configured Flask app
    """

    flask_app = Flask(__name__)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
    )
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["CACHE_TYPE"] = "SimpleCache"

    if test_config:
        flask_app.config.update(test_config)

    cache.init_app(flask_app)
    db.init_app(flask_app)

    flask_app.register_blueprint(bp)

    if not flask_app.debug and not flask_app.testing:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        log_filename = datetime.now().strftime("logs/app_%Y-%m-%d.log")
        handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1)
        handler.suffix = "%Y-%m-%d"
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        )

        flask_app.logger.addHandler(handler)
        flask_app.logger.addHandler(logging.StreamHandler())

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("DEBUG", "True") == "True")
