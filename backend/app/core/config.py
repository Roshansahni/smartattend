"""
Application configuration loaded from environment variables.
Uses Pydantic Settings for type-safe config management.
"""
from functools import lru_cache
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """All application settings loaded from .env file."""
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://smartattend:password@localhost:5432/smartattend_db"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "smartattend_db"
    db_user: str = "smartattend"
    db_password: str = "password"

    # JWT
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-32-CHAR-MIN"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # App
    app_name: str = "SmartAttend"
    debug: bool = True
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # QR
    qr_token_expire_seconds: int = 30
    qr_refresh_interval_seconds: int = 25

    # GPS
    gps_default_radius_meters: int = 100
    gps_enabled: bool = True

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Returns cached settings instance. Use as FastAPI dependency."""
    return Settings()
