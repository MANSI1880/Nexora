import pytest
import pytest_asyncio
import time
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_user(async_client):
    username = f"user_{time.time()}"
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

@pytest_asyncio.fixture
async def auth_user_2(async_client):
    username = f"user2_{time.time()}"
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
async def test_create_ticket(async_client, auth_user):
    response = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "VPN down"
    assert data["status"] == "OPEN"
    assert "id" in data

@pytest.mark.asyncio
async def test_unauthenticated_ticket_creation_rejected(async_client):
    response = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_user_can_view_own_ticket(async_client, auth_user):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.get(
        f"/api/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id

@pytest.mark.asyncio
async def test_user_cannot_view_another_users_ticket(async_client, auth_user, auth_user_2):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "My VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.get(
        f"/api/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {auth_user_2['token']}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_authorized_update(async_client, auth_user):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

@pytest.mark.asyncio
async def test_unauthorized_update_rejected(async_client, auth_user, auth_user_2):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {auth_user_2['token']}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_ticket_not_found(async_client, auth_user):
    response = await async_client.get(
        f"/api/tickets/999999",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 404
