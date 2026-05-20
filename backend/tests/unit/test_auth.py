"""
tests/unit/test_auth.py

Tests for authentication endpoints: register, login, profile.
"""

import pytest
from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "full_name": "Jane QA",
            "email": "jane@qpilot.ai",
            "password": "securepass123",
            "role": "qa_engineer",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["email"] == "jane@qpilot.ai"
        assert data["data"]["role"] == "qa_engineer"
        assert "hashed_password" not in data["data"]

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/register", json={
            "full_name": "Duplicate",
            "email": "test@qpilot.ai",   # same as test_user
            "password": "securepass123",
        })
        assert resp.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "full_name": "Bad Email",
            "email": "not-an-email",
            "password": "securepass123",
        })
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "full_name": "Short Pass",
            "email": "short@qpilot.ai",
            "password": "abc",
        })
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@qpilot.ai",
            "password": "testpassword123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@qpilot.ai",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@qpilot.ai",
            "password": "somepassword",
        })
        assert resp.status_code == 401


class TestProfile:
    async def test_profile_authenticated(self, auth_client: AsyncClient, test_user):
        resp = await auth_client.get("/api/v1/auth/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["email"] == test_user.email

    async def test_profile_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/profile")
        assert resp.status_code == 401
