
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "OpsPilot AI"
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_diagnose_rejects_empty_log():
    response = client.post(
        "/incidents/diagnose",
        json={"log_line": "", "top_k": 3},
    )

    assert response.status_code == 422


def test_diagnose_rejects_invalid_top_k():
    response = client.post(
        "/incidents/diagnose",
        json={
            "log_line": (
                "081109 203518 143 INFO "
                "dfs.DataNode$DataXceiver: Receiving block"
            ),
            "top_k": 20,
        },
    )

    assert response.status_code == 422
