import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, Base
from app.db.database import get_db
from app.core.config import settings

engine = create_engine(settings.TEST_DB_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture Scope Levels
# scope='function' (Default): Runs once per test function.
# scope='class': Runs once per test class.
# scope='module': Runs once per module (file).
# scope='package': Runs once per package.
# scope='session': Runs once per test session
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine):
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSession(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Override get_db dependency and return a TestClient."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
