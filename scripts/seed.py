#!/usr/bin/env python3
"""
scripts/seed.py

Seed the database with a default admin user for development.

Usage:
    cd backend
    python ../scripts/seed.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    from app.core.config import settings
    from app.models.models import User

    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "admin@qpilot.ai"))
        existing = result.scalar_one_or_none()

        if existing:
            print("✓ Admin user already exists.")
        else:
            admin = User(
                full_name="QPilot Admin",
                email="admin@qpilot.ai",
                hashed_password=pwd_context.hash("qpilot123"),
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            print("✓ Admin user created: admin@qpilot.ai / qpilot123")

        # Also create a QA engineer user
        result = await session.execute(select(User).where(User.email == "qa@qpilot.ai"))
        existing_qa = result.scalar_one_or_none()

        if not existing_qa:
            qa_user = User(
                full_name="QA Engineer",
                email="qa@qpilot.ai",
                hashed_password=pwd_context.hash("qpilot123"),
                role="qa_engineer",
                is_active=True,
            )
            session.add(qa_user)
            await session.commit()
            print("✓ QA user created: qa@qpilot.ai / qpilot123")

    await engine.dispose()
    print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
