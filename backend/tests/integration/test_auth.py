import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

class TestAuth:
    async def test_health(self, client: AsyncClient):
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

    async def test_protected_unauthorized(self, client: AsyncClient):
        res = await client.get("/api/v1/users/me")
        assert res.status_code in (401, 403)
