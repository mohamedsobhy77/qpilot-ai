"""
tests/conftest.py

Pytest fixtures shared across all tests.
Uses an in-memory SQLite database so tests run without PostgreSQL.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app
from app.models.models import User
from app.core.security import hash_password, create_access_token

# ── Test DB (in-memory SQLite) ────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Yield a live database session for tests that need direct DB access."""
    async with TestAsyncSession() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a test user."""
    user = User(
        full_name="Test QA Engineer",
        email="test@qpilot.ai",
        hashed_password=hash_password("testpassword123"),
        role="qa_engineer",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Return a valid JWT token for the test user."""
    return create_access_token(subject=str(test_user.id))


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """AsyncClient with the test DB injected via dependency override."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, auth_token: str) -> AsyncClient:
    """AsyncClient with Authorization header pre-set."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
