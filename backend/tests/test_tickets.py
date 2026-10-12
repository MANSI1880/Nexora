import pytest
import pytest_asyncio
import time
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.database.connection import AsyncSessionLocal
from app.models.user import User
from app.models.approval import Approval
from app.models.ticket import Ticket
from app.services import ticket as ticket_service
from app.schemas.ticket import TicketCreate

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

@pytest_asyncio.fixture
async def it_support_user(async_client):
    username = f"support_{time.time()}"
    password = "securepassword123"
    await async_client.post(
        "/api/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": password}
    )
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        db_user = result.scalars().first()
        db_user.role = "it_support"
        await session.commit()

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
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"

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
        json={"title": "VPN down - Urgent", "description": "Cannot connect to VPN after reinstall"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "VPN down - Urgent"
    assert data["description"] == "Cannot connect to VPN after reinstall"

@pytest.mark.asyncio
async def test_ordinary_user_cannot_update_status(async_client, auth_user):
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
    assert response.status_code == 403
    assert "Only IT Support or Admin can alter ticket status or priority" in response.json()["detail"]

@pytest.mark.asyncio
async def test_ordinary_user_cannot_update_priority(async_client, auth_user):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.put(
        f"/api/tickets/{ticket_id}",
        json={"priority": "CRITICAL"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 403
    assert "Only IT Support or Admin can alter ticket status or priority" in response.json()["detail"]

@pytest.mark.asyncio
async def test_staff_can_update_status_and_priority(async_client, auth_user, it_support_user):
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "VPN down", "description": "Cannot connect to VPN", "priority": "HIGH"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS", "priority": "CRITICAL"},
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["priority"] == "CRITICAL"

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
        json={"title": "Hacked title"},
        headers={"Authorization": f"Bearer {auth_user_2['token']}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"

@pytest.mark.asyncio
async def test_ticket_not_found(async_client, auth_user):
    response = await async_client.get(
        f"/api/tickets/999999",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_authorized_approval(async_client, auth_user, it_support_user):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == auth_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Need new laptop", description="Dev laptop requested", priority="HIGH"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    response = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"

    async with AsyncSessionLocal() as session:
        approval = await ticket_service.get_approval_by_ticket_id(session, ticket_id)
        assert approval is not None
        assert approval.status == "APPROVED"

@pytest.mark.asyncio
async def test_authorized_rejection(async_client, auth_user, it_support_user):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == auth_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Need extra monitor", description="Second monitor", priority="LOW"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    response = await async_client.post(
        f"/api/tickets/{ticket_id}/reject",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"

    async with AsyncSessionLocal() as session:
        approval = await ticket_service.get_approval_by_ticket_id(session, ticket_id)
        assert approval is not None
        assert approval.status == "DENIED"

@pytest.mark.asyncio
async def test_unauthorized_user_cannot_approve(async_client, auth_user, auth_user_2):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == auth_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Need new laptop", description="Dev laptop", priority="HIGH"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    response = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {auth_user_2['token']}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_requester_cannot_approve_own_ticket(async_client, it_support_user):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == it_support_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Self hardware request", description="Testing self approval", priority="HIGH"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    response = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert response.status_code == 403
    assert "Requesters cannot approve their own tickets" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_transition_approval(async_client, auth_user, it_support_user):
    # Test approving an OPEN ticket
    create_resp = await async_client.post(
        "/api/tickets",
        json={"title": "General issue", "description": "Not an approval ticket", "priority": "LOW"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    ticket_id = create_resp.json()["id"]

    response = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert response.status_code == 400
    assert "cannot be approved in 'OPEN' status" in response.json()["detail"]

@pytest.mark.asyncio
async def test_conflicting_approval_decision_rejected(async_client, auth_user, it_support_user):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == auth_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Conflicting test ticket", description="Testing conflicts", priority="MEDIUM"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    approve_resp = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"

    reject_resp = await async_client.post(
        f"/api/tickets/{ticket_id}/reject",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert reject_resp.status_code == 400
    assert "cannot be rejected in 'APPROVED' status" in reject_resp.json()["detail"]

    reapprove_resp = await async_client.post(
        f"/api/tickets/{ticket_id}/approve",
        headers={"Authorization": f"Bearer {it_support_user['token']}"}
    )
    assert reapprove_resp.status_code == 400
    assert "cannot be approved in 'APPROVED' status" in reapprove_resp.json()["detail"]

@pytest.mark.asyncio
async def test_concurrent_conflicting_decisions_race(async_client, auth_user, it_support_user):
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == auth_user["username"]))
        u = user_res.scalars().first()
        db_ticket = await ticket_service.create_ticket(
            session,
            TicketCreate(title="Race test ticket", description="Testing concurrency", priority="MEDIUM"),
            user_id=u.id,
            status="PENDING_APPROVAL"
        )
        ticket_id = db_ticket.id

    results = await asyncio.gather(
        async_client.post(
            f"/api/tickets/{ticket_id}/approve",
            headers={"Authorization": f"Bearer {it_support_user['token']}"}
        ),
        async_client.post(
            f"/api/tickets/{ticket_id}/reject",
            headers={"Authorization": f"Bearer {it_support_user['token']}"}
        )
    )

    statuses = [r.status_code for r in results]
    assert statuses.count(200) == 1
    assert any(s in [400, 409] for s in statuses)
