import pytest
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
