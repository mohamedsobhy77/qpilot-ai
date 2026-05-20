"""
app/db/database.py

Async SQLAlchemy engine and session factory.
Use get_db() as a FastAPI dependency to get a DB session per request.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create the async engine — connection pool is managed automatically
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,          # Log SQL statements in dev
    pool_pre_ping=True,            # Verify connections before use
    pool_size=10,
    max_overflow=20,
)

# Session factory — each request gets its own session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,        # Keep attributes accessible after commit
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.
    Session is committed on success and rolled back on exception.

    Usage in a router:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
