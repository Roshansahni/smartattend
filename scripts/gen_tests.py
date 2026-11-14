from pathlib import Path

ROOT = Path("/Users/roshansahni/.gemini/antigravity/scratch/smartattend/backend")

files = {}

files["pytest.ini"] = """[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
"""

files["tests/__init__.py"] = ""
files["tests/unit/__init__.py"] = ""
files["tests/integration/__init__.py"] = ""

files["tests/unit/test_security.py"] = """import pytest
from datetime import datetime, timezone
from jose import JWTError
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_qr_token
)

class TestSecurity:
    def test_password_hash(self):
        h = get_password_hash("Password123")
        assert verify_password("Password123", h) is True
        assert verify_password("WrongPassword", h) is False

    def test_jwt_token(self):
        t = create_access_token(subject="user-1", role="faculty")
        payload = decode_token(t)
        assert payload["sub"] == "user-1"
        assert payload["role"] == "faculty"

    def test_qr_token_uniqueness(self):
        tokens = {generate_qr_token() for _ in range(50)}
        assert len(tokens) == 50
"""

files["tests/unit/test_gps.py"] = """from app.utils.gps import calculate_distance, is_within_radius

class TestGPS:
    def test_distance_zero(self):
        assert calculate_distance(28.0, 77.0, 28.0, 77.0) == 0.0

    def test_radius_check(self):
        within, dist = is_within_radius(28.5450, 77.1926, 28.5452, 77.1926, 100)
        assert within is True
        assert dist < 100
"""

files["tests/unit/test_qr.py"] = """from app.utils.qr_generator import generate_qr_image

def test_qr_generation():
    img = generate_qr_image("sample-token")
    assert img.startswith("data:image/png;base64,")
"""

files["tests/integration/test_auth.py"] = """import pytest
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
"""

for rel_path, content in files.items():
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Written: {rel_path}")

print("Tests generated successfully.")
