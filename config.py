# config.py
import os

locations = {
    "Bicocca": "bicocca.db",
    "Meda": "meda.db",
    "Torino": "torino.db",
    "Marcianise": "marcianise.db",
    "Catania": "catania.db",
    "Udine": "udine.db"
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")

SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))