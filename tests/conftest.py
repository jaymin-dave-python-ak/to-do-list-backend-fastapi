import pytest
import fakeredis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock

from app.main import app, Base
from app.api.v1.dependencies import get_db, get_redis, EmailService
from app.core.config import settings

engine = create_engine(settings.TEST_DB_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
global_fake_redis = fakeredis.FakeRedis()


@pytest.fixture(scope="session")
def db_engine():
    """Build the test database structure before any tests run and destroy it after."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine):
    """Create a temporary database session that undoes all changes after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSession(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Setup a test client with fake database, email, and redis services."""

    def override_get_db():
        """Swap the real database for the isolated test database."""
        yield db

    def override_get_redis():
        """Swap the real Redis server for a fake in-memory version."""
        return global_fake_redis

    # Create mock email service
    mock_email_instance = EmailService()
    mock_email_instance.send_otp_email = AsyncMock(return_value=None)

    # Apply all overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[EmailService] = lambda: mock_email_instance

    with TestClient(app) as c:
        yield c

    # Reset for the next test
    app.dependency_overrides.clear()
    global_fake_redis.flushall()