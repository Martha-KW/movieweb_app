import pytest
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Temporärer Pfad-Fix (ESSENTIELL)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

# Absolute Imports NACH dem sys.path-Update
from models import User, Movie
from data_manager.sqlite_data_manager import SQLiteDataManager
from app import create_app

@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def test_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    yield app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def init_db(test_app):
    dm = test_app.config['DATA_MANAGER'] = SQLiteDataManager('sqlite:///:memory:')
    session = dm.Session()
    try:
        test_user = User(username="test_user")
        session.add(test_user)
        session.commit()
    finally:
        session.close()
