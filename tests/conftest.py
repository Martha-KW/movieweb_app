
import pytest
import os
from app import app
from data_manager.sqlite_data_manager import SQLiteDataManager

@pytest.fixture(scope='session')
def test_db_path(tmp_path_factory):
    """Erstellt eine temporäre Kopie der DB für Tests."""
    original_db = "data/movies.db"
    test_db = tmp_path_factory.mktemp("data") / "test_movies.db"

    # Kopiere die originale DB (falls benötigt)
    if os.path.exists(original_db):
        import shutil
        shutil.copy(original_db, test_db)

    return test_db


@pytest.fixture
def test_client():
    # Setze TESTING-Umgebungsvariable
    import os
    os.environ['TESTING'] = 'true'

    # Erstelle einen neuen DataManager mit In-Memory-DB
    app.config['DATA_MANAGER'] = SQLiteDataManager()  # 👈 Nutzt automatisch :memory:

    with app.test_client() as client:
        yield client
