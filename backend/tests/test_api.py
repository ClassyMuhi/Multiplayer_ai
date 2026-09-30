import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Summit" in data["service"]
    assert data["database"] == "connected"



def test_list_and_create_projects(client):
    # List projects (startup should have initialized demo-calculator)
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert any(p["id"] == "demo-calculator" for p in data["projects"])

    # Create new project
    create_res = client.post("/api/projects", json={"name": "Test Project", "template": "demo-calculator"})
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "Test Project"
    new_id = created_data["id"]

    # Fetch newly created project
    get_res = client.get(f"/api/projects/{new_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == new_id


def test_file_operations_api(client):
    project_id = "demo-calculator"

    # List files
    tree_res = client.get(f"/api/projects/{project_id}/files")
    assert tree_res.status_code == 200
    tree = tree_res.json()
    assert any(node["name"] == "calculator.py" for node in tree)

    # Read file
    read_res = client.get(f"/api/projects/{project_id}/files/calculator.py")
    assert read_res.status_code == 200
    content_data = read_res.json()
    assert "def add" in content_data["content"]

    # Update file
    new_content = '"""Updated calculator"""\ndef add(a, b): return a + b\n'
    put_res = client.put(
        f"/api/projects/{project_id}/files/calculator.py",
        json={"content": new_content}
    )
    assert put_res.status_code == 200

    # Verify updated content
    verify_res = client.get(f"/api/projects/{project_id}/files/calculator.py")
    assert verify_res.status_code == 200
    assert "Updated calculator" in verify_res.json()["content"]


def test_agent_status_api(client):
    project_id = "demo-calculator"
    status_res = client.get(f"/api/projects/{project_id}/agent/status")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["project_id"] == project_id
    assert "status" in data

