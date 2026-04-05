import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, engine, Base

client = TestClient(app)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_task():
    """Test task creation"""
    task_data = {
        "title": "Test Task",
        "description": "Test description",
        "priority": "high",
        "due_date": "2024-12-31T23:59:59",
        "assigned_to": "Test User"
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_tasks():
    """Test getting tasks list"""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)