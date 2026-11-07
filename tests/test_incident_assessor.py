
from app.services.incident_assessor import assess_incident


def test_anomaly_assessment_does_not_claim_root_cause():
    incident = {
        "component": "dfs.DataNode",
        "level": "ERROR",
        "message": "Block replication failed",
    }

    prediction = {
        "is_anomaly": True,
        "prediction": "anomaly",
        "anomaly_score": 0.25,
    }

    result = assess_incident(
        incident=incident,
        prediction=prediction,
        runbooks=[],
    )

    assert result["status"] == "anomaly_flagged"
    assert result["root_cause"] is None
    assert result["matching_runbooks"] == 0
    assert len(result["recommendations"]) > 0


def test_normal_assessment_does_not_guarantee_health():
    result = assess_incident(
        incident={"component": "dfs.DataNode", "level": "INFO"},
        prediction={
            "is_anomaly": False,
            "prediction": "normal",
            "anomaly_score": -0.1,
        },
        runbooks=[],
    )

    assert result["status"] == "no_anomaly_flagged"
    assert "does not guarantee" in result["summary"]
