import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_sqlite_persistence_and_memories(client):
    project_id = "demo-calculator"

    # Add memory item
    mem_res = client.post(
        f"/api/projects/{project_id}/memory",
        json={"key": "ArchDecision", "value": "Use SQLite persistence", "category": "architecture"}
    )
    assert mem_res.status_code == 201
    mem_data = mem_res.json()
    assert mem_data["key"] == "ArchDecision"
    assert mem_data["category"] == "architecture"

    # Retrieve memories
    get_mem = client.get(f"/api/projects/{project_id}/memory")
    assert get_mem.status_code == 200
    memories = get_mem.json()["memories"]
    assert any(m["key"] == "ArchDecision" for m in memories)


def test_file_versioning_and_conflict_detection(client):
    project_id = "demo-calculator"
    file_path = "calculator.py"

    # Read current file to get version
    read_res = client.get(f"/api/projects/{project_id}/files/{file_path}")
    assert read_res.status_code == 200
    orig = read_res.json()
    v1 = orig["version"]

    # User A updates file to v2
    put_a = client.put(
        f"/api/projects/{project_id}/files/{file_path}",
        json={"content": orig["content"] + "\n# User A edit\n", "expected_version": v1, "user_id": "user_a"}
    )
    assert put_a.status_code == 200
    assert put_a.json()["version"] == v1 + 1

    # User B attempts to save based on stale v1 (Conflict expected!)
    put_b = client.put(
        f"/api/projects/{project_id}/files/{file_path}",
        json={"content": orig["content"] + "\n# User B edit\n", "expected_version": v1, "user_id": "user_b"}
    )
    assert put_b.status_code == 409
    detail = put_b.json()["detail"]
    assert detail["conflict"] is True
    assert detail["server_version"] == v1 + 1
    assert detail["expected_version"] == v1


def test_git_checkpoints_api(client):
    project_id = "demo-calculator"

    # Fetch status
    status_res = client.get(f"/api/projects/{project_id}/git/status")
    assert status_res.status_code == 200
    assert "branch" in status_res.json()

    # Create checkpoint
    chk_res = client.post(
        f"/api/projects/{project_id}/git/checkpoint",
        json={"message": "Test checkpoint commit"}
    )
    assert chk_res.status_code == 200
    assert "commit_hash" in chk_res.json()


def test_connected_users_api(client):
    project_id = "demo-calculator"
    res = client.get(f"/api/projects/{project_id}/users")
    assert res.status_code == 200
    assert "users" in res.json()


def test_agent_pause_resume_stop_api(client):
    project_id = "demo-calculator"

    # Agent is idle initially
    res_pause = client.post(f"/api/projects/{project_id}/agent/pause")
    assert res_pause.status_code == 200

    res_stop = client.post(f"/api/projects/{project_id}/agent/stop")
    assert res_stop.status_code == 200
