
from fastapi.testclient import TestClient

from app.main import app
import app.api.incidents as incidents_api


client = TestClient(app)

SAMPLE_LOG = (
    "081109 203518 143 INFO "
    "dfs.DataNode$DataXceiver: Receiving block "
    "blk_-1608999687919862906 "
    "src: /10.250.19.102:54106 "
    "dest: /10.250.19.102:50010"
)


def fake_diagnosis(llm_status="success"):
    explanation = (
        "The log was analyzed. Further investigation is recommended."
        if llm_status == "success"
        else None
    )

    return {
        "status": "anomaly_flagged",
        "incident": {
            "component": "dfs.DataNode$DataXceiver",
            "level": "INFO",
            "message": "Receiving block",
        },
        "analysis": {
            "parsed_log": {},
            "features": {},
            "prediction": {
                "is_anomaly": True,
                "prediction": "anomaly",
                "anomaly_score": 0.25,
                "score_note": "Higher scores indicate more unusual records.",
            },
        },
        "troubleshooting": {
            "query": "HDFS block",
            "results_count": 0,
            "runbooks": [],
            "message": "No matching runbooks found.",
        },
        "assessment": "The model flagged this record as unusual.",
        "incident_assessment": {
            "status": "anomaly_flagged",
            "summary": "The model flagged this record as unusual.",
            "component": "dfs.DataNode$DataXceiver",
            "log_level": "INFO",
            "observed_message": "Receiving block",
            "anomaly_score": 0.25,
            "matching_runbooks": 0,
            "root_cause": None,
            "recommendations": ["Inspect nearby logs."],
            "limitations": ["An anomaly flag does not confirm an incident."],
        },
        "llm_explanation": explanation,
        "llm_status": llm_status,
        "llm_error": (
            None
            if llm_status == "success"
            else "AI explanation unavailable."
        ),
        "evidence_available": False,
        "limitations": ["An anomaly flag does not confirm an incident."],
    }


def test_diagnose_api_with_llm_success(monkeypatch):
    monkeypatch.setattr(
        incidents_api,
        "run_diagnosis",
        lambda log_line, top_k: fake_diagnosis("success"),
    )

    response = client.post(
        "/incidents/diagnose",
        json={"log_line": SAMPLE_LOG, "top_k": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["llm_status"] == "success"
    assert data["llm_explanation"]
    assert data["analysis"]["prediction"]["is_anomaly"] is True


def test_diagnose_api_when_llm_unavailable(monkeypatch):
    monkeypatch.setattr(
        incidents_api,
        "run_diagnosis",
        lambda log_line, top_k: fake_diagnosis("unavailable"),
    )

    response = client.post(
        "/incidents/diagnose",
        json={"log_line": SAMPLE_LOG, "top_k": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["llm_status"] == "unavailable"
    assert data["llm_explanation"] is None
    assert data["assessment"]
    assert data["analysis"]


def test_diagnose_api_rejects_invalid_top_k():
    response = client.post(
        "/incidents/diagnose",
        json={"log_line": SAMPLE_LOG, "top_k": 20},
    )

    assert response.status_code == 422
