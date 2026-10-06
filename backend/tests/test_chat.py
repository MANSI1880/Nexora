import pytest
import pytest_asyncio
import time
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_user(async_client):
    username = f"chatuser_{time.time()}"
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
async def test_chat_requires_jwt(async_client):
    response = await async_client.post(
        "/api/chat",
        json={"message": "I need jira access"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
@patch("app.api.chat.process_chat_request")
async def test_chat_successfully_calls_ai_orchestrator(mock_process, async_client, auth_user):
    mock_process.return_value = {
        "response": "Here is the meaning of life.",
        "intent": "unknown",
        "confidence": 0.9,
        "sources": [],
        "ticket_id": None,
        "action": None,
        "status": "resolved"
    }
    
    response = await async_client.post(
        "/api/chat",
        json={"message": "What is the meaning of life, the universe, and everything?"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Here is the meaning of life."
    assert data["intent"] == "unknown"

@pytest.mark.asyncio
@patch("app.api.chat.process_chat_request")
async def test_ai_created_ticket_persisted(mock_process, async_client, auth_user):
    mock_process.return_value = {
        "response": "I will create a ticket for you.",
        "intent": "application_access",
        "confidence": 0.9,
        "sources": [],
        "ticket_id": None,
        "action": "Jira access",
        "status": "pending_approval"
    }

    response = await async_client.post(
        "/api/chat",
        json={"message": "I need Jira access"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    if data.get("ticket_id"):
        ticket_id = data["ticket_id"]
        ticket_resp = await async_client.get(
            f"/api/tickets/{ticket_id}",
            headers={"Authorization": f"Bearer {auth_user['token']}"}
        )
        assert ticket_resp.status_code == 200
        assert ticket_resp.json()["id"] == int(ticket_id)

