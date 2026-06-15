# app/test/conftest.py
import sys
from pathlib import Path

# Add the root 'backend' directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app  # Import your FastAPI app instance
from database.base import Base  # Adjust imports to match your base database file
from database.connection import get_db_session  # Import the original dependency to override

# 1. Setup an isolated SQLite in-memory test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, future=True)

# 2. Create the session factory with expire_on_commit=False to prevent db.refresh() errors
TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False  
)

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Overrides pytest-asyncio's default loop to handle session scopes properly."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Drops and rebuilds clean database tables before every individual test function."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 3. Cleanly yield the session without forcing extra transaction constraints
async def override_get_db_session():
    async with TestingSessionLocal() as session:
        yield session

# 4. Apply the database session override to your FastAPI app instance
@pytest.fixture(scope="function", autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db_session] = override_get_db_session
    yield
    app.dependency_overrides.clear()

# 5. Provide an AsyncClient fixture using modern HTTPX ASGITransport syntax
@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac