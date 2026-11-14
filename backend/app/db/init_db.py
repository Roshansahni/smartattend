"""Initialize database tables directly (supports both SQLite and PostgreSQL)."""
import asyncio
from app.db.base import Base
from app.db.session import engine
import app.models  # Load all models

async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_tables())
