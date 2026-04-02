import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use a separate SQLite file for tests (reset between each test function)
TEST_DATABASE_URL = "sqlite:///./test_finance.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before every test for full isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Log in as the seeded admin and return the raw JWT string."""
    r = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin@123!"},
    )
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def viewer_headers(client, admin_headers):
    """Create a viewer user and return its auth headers."""
    client.post(
        "/users",
        headers=admin_headers,
        json={
            "email": "viewer@test.com",
            "full_name": "Test Viewer",
            "password": "Viewer@123!",
            "role": "viewer",
        },
    )
    r = client.post(
        "/auth/login",
        json={"email": "viewer@test.com", "password": "Viewer@123!"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def analyst_headers(client, admin_headers):
    """Create an analyst user and return its auth headers."""
    client.post(
        "/users",
        headers=admin_headers,
        json={
            "email": "analyst@test.com",
            "full_name": "Test Analyst",
            "password": "Analyst@123!",
            "role": "analyst",
        },
    )
    r = client.post(
        "/auth/login",
        json={"email": "analyst@test.com", "password": "Analyst@123!"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def sample_record_payload():
    return {
        "amount": 5000.00,
        "record_type": "income",
        "category": "salary",
        "record_date": "2024-06-15",
        "description": "Monthly salary",
        "notes": "June paycheck",
    }