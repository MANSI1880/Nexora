import pytest
import pytest_asyncio
import time
import os
from dotenv import load_dotenv
load_dotenv(".env")
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url="http://127.0.0.1:8000", timeout=30.0) as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_user(async_client):
    username = f"e2euser_{time.time()}"
    password = "securepassword123"
    await async_client.post(
        "/api/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": password}
    )
    login_resp = await async_client.post(
        "/api/auth/login",
        data={"username": username, "password": password}
    )
    token = login_resp.json()["access_token"]
    return {"token": token, "username": username}

@pytest.mark.asyncio
async def test_vpn_troubleshooting_rag(async_client, auth_user):
    """VPN troubleshooting -> RAG response."""
    response = await async_client.post(
        "/api/chat",
        json={"message": "My VPN is not working. How do I fix it?"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "vpn_troubleshooting"
    assert data["status"] == "resolved"
    assert data["ticket_id"] is None

@pytest.mark.asyncio
async def test_explicit_laptop_request_ticket(async_client, auth_user):
    """Explicit laptop request -> ticket creation."""
    response = await async_client.post(
        "/api/chat",
        json={"message": "I need a new laptop"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "hardware_request"
    assert data["status"] == "pending_approval"
    assert data["ticket_id"] is not None

    # Verify ticket in DB
    ticket_resp = await async_client.get(
        f"/api/tickets/{data['ticket_id']}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert ticket_resp.status_code == 200
    assert ticket_resp.json()["id"] == int(data["ticket_id"])

@pytest.mark.asyncio
async def test_general_it_question_no_ticket(async_client, auth_user):
    """General IT question -> no unnecessary ticket."""
    response = await async_client.post(
        "/api/chat",
        json={"message": "What is the best way to write an email?"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] in ["email_issue", "general_it_support", "unknown"]
    # If it's a general question, it should be resolved or escalated safely depending on confidence
    # But it shouldn't just automatically create an action ticket.
    if data["status"] == "resolved":
        assert data["ticket_id"] is None

@pytest.mark.asyncio
async def test_unknown_intent_escalation(async_client, auth_user):
    """Unknown intent -> existing safe escalation behavior."""
    response = await async_client.post(
        "/api/chat",
        json={"message": "jkfldjsaklghdfksahgkfas"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "unknown"
    assert data["status"] == "needs_escalation"
    assert data["ticket_id"] is not None
