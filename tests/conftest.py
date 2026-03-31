import uuid
from collections.abc import AsyncGenerator
from uuid import uuid7

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # pyright: ignore[reportMissingTypeStubs]

from app.api import app
from app.core.authn.dependencies import get_current_user
from app.core.authn.entities import User
from app.core.database.engine import get_session
from app.core.database.models.base import Base
from app.utils.time_utils import now_utc


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:18", driver="asyncpg") as pg:
        yield pg


@pytest.fixture
async def db_session(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncSession]:
    schema = f"test_{uuid.uuid4().hex[:8]}"
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url)

    original_schema = Base.metadata.schema
    Base.metadata.schema = schema

    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA {schema}"))
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))

    Base.metadata.schema = original_schema
    await engine.dispose()


@pytest.fixture
def fake_user():
    now = now_utc()
    return User(
        id=uuid7(),
        auth_provider_id=f"test-{uuid.uuid4().hex[:8]}",
        name="Test User",
        avatar_url=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
async def authenticated_client(
    db_session: AsyncSession, fake_user: User
) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
