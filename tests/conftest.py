import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fakeredis import FakeServer
from fakeredis.aioredis import FakeRedis
from unittest.mock import AsyncMock
from sqlalchemy.pool import NullPool

from app.main import app, Base
from app.api.v1.dependencies import get_db, get_redis, EmailService
from app.core.config import settings

engine = create_async_engine(
    settings.TEST_DB_URL,
    future=True,
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

shared_server = FakeServer()
global_fake_redis = FakeRedis(server=shared_server, decode_responses=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def db_engine():
    """Create tables at the start of the session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    

@pytest.fixture
async def db():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.close()

        await transaction.rollback()


@pytest.fixture
async def client(db):
    """Setup an async test client with overrides."""
    mock_email_instance = EmailService()
    mock_email_instance.send_otp_email = AsyncMock(return_value=None)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_redis] = lambda: global_fake_redis
    app.dependency_overrides[EmailService] = lambda: mock_email_instance

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    await global_fake_redis.flushall()