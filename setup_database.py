""" Run this file to setup a totally new and empty database after installing the
app or resetting all data."""
import os
from sqlalchemy import create_engine
from models import Base  # <- dein Base kommt aus models.py

# Path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "movies.db")
DB_URI = f"sqlite:///{DB_PATH}"

# create an engine
engine = create_engine(DB_URI)

# create the tables
Base.metadata.create_all(engine)

print(f"SQLAlchemy-based database created at {DB_PATH}")
