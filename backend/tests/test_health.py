import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app, get_cors_origins

@pytest.mark.asyncio
async def test_health_endpoint_success():
    with patch("app.main.AsyncSessionLocal") as mock_session_local:
        mock_session = AsyncMock()
        mock_session_local.return_value = mock_session

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy", "database": "connected"}

@pytest.mark.asyncio
async def test_health_endpoint_live_db_probing():
    # Tests un-mocked live probe against the configured database
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            assert response.json() == {"status": "healthy", "database": "connected"}
        else:
            assert response.json() == {"status": "unhealthy", "database": "disconnected"}


@pytest.mark.asyncio
async def test_health_endpoint_db_failure():
    with patch("app.main.AsyncSessionLocal") as mock_session_local:
        mock_session = AsyncMock()
        mock_session.__aenter__.side_effect = Exception("DB Connection Refused")
        mock_session_local.return_value = mock_session

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert data == {"status": "unhealthy", "database": "disconnected"}
            # Ensure internal error message is not leaked in response
            assert "DB Connection Refused" not in str(data)

def test_cors_default_fallback():
    assert get_cors_origins(None) == ["http://localhost:3000", "http://127.0.0.1:3000"]
    assert get_cors_origins("") == ["http://localhost:3000", "http://127.0.0.1:3000"]
    assert get_cors_origins("   ") == ["http://localhost:3000", "http://127.0.0.1:3000"]

def test_cors_custom_origins():
    origins = get_cors_origins("https://nexora.vercel.app, https://app.nexora.com")
    assert origins == ["https://nexora.vercel.app", "https://app.nexora.com"]

def test_cors_excludes_wildcard_origin():
    # Disallowing wildcard when credentials enabled
    assert get_cors_origins("*") == ["http://localhost:3000", "http://127.0.0.1:3000"]
    origins_mixed = get_cors_origins("https://nexora.vercel.app, *, https://app.nexora.com")
    assert origins_mixed == ["https://nexora.vercel.app", "https://app.nexora.com"]
