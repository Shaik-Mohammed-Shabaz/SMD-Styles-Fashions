import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATABASE_PATH = os.path.join(BASE_DIR, "database", "smd_fashion.db")

class Config:
    SECRET_KEY = "smd-styles-fashions-dev-key-2026"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False