
import os
from sqlalchemy import create_engine
from models import Base  # <- dein Base kommt aus models.py

# Datenbankpfad
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "movies.db")
DB_URI = f"sqlite:///{DB_PATH}"

# Engine erzeugen
engine = create_engine(DB_URI)

# Tabellen anlegen
Base.metadata.create_all(engine)

print(f"SQLAlchemy-based database created at {DB_PATH}")
