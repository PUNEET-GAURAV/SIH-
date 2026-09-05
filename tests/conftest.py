"""Pytest configuration and fixtures."""

import os
import sys
import pytest
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Use SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_docshield.db"
os.environ["MOCK_MODE"] = "false"
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import get_db
from backend.models import Base


# Test database
TEST_DB_URL = "sqlite:///./test_docshield.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    # Clean up test DB file
    db_file = Path("./test_docshield.db")
    try:
        if db_file.exists():
            db_file.unlink()
    except PermissionError:
        pass  # Windows file locking — cleaned up next run


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Get a test HTTP client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a test user and return auth headers."""
    # Register
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "officer",
    })

    # Login
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
