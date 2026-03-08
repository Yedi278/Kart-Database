import os
from database import Database
from config import DB_DIR, locations
from utils.decorators import login_required
from flask import session


def get_db():
    location = session.get("location")

    if not location or location not in locations:
        return None

    db_path = os.path.join(DB_DIR, locations[location])
    return Database(db_path)