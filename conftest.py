import os
import pytest
from cafeto.testclient import TestClient

@pytest.fixture()
def setup_app():
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_SILENCE_UBER_WARNING = os.getenv("SQLALCHEMY_SILENCE_UBER_WARNING")

    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

    from main import app, base_ormar_config, engine

    client = TestClient(app)

    base_ormar_config.metadata.drop_all(engine)
    base_ormar_config.metadata.create_all(engine)

    yield client

    base_ormar_config.metadata.drop_all(engine)
    if DATABASE_URL:
        os.environ['DATABASE_URL'] = DATABASE_URL
    
    if SQLALCHEMY_SILENCE_UBER_WARNING:
        os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = SQLALCHEMY_SILENCE_UBER_WARNING
