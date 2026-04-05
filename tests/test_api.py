import pytest
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_api_root():
    """Test API root endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_create_and_delete_task():
    """Test full task lifecycle"""
    # Create task
    task = {
        "title": "Lifecycle Test",
        "due_date": "2024-12-31T23:59:59"
    }
    create_response = client.post("/tasks", json=task)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Get task
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    
    # Update task
    update_response = client.put(f"/tasks/{task_id}", json={"status": "completed"})
    assert update_response.status_code == 200
    
    # Delete task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204