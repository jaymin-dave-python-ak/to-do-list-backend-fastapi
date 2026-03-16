import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, Base
from app.api.v1.dependencies import DBDep
from app.core.config import settings

engine = create_engine(settings.TEST_DB_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine and setup/drop tables for the entire pytest session."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine):
    """Provide an isolated SQLAlchemy database session wrapped in a transaction for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSession(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Return FastAPI TestClient with overridden get_db dependency to use the test database session."""

    def override_get_db():
        yield db

    app.dependency_overrides[DBDep] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# from unittest.mock import AsyncMock, patch
# import pytest


# @pytest.fixture(autouse=True)
# # Using autouse=True ensures no real emails are sent during any test.
# def mock_email_service():
#     """
#     Globally mocks the EmailService.send_otp_email method.
#     """
#     with patch(
#         "app.service.email_service.EmailService.send_otp_email", new_callable=AsyncMock
#     ) as mock_send:
#         yield mock_send
