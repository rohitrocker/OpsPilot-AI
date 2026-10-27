
from app.agents.workflow import run_diagnosis


def test_diagnosis_returns_structured_assessment():
    log_line = (
        "081109 203518 143 INFO "
        "dfs.DataNode$DataXceiver: Receiving block "
        "blk_-1608999687919862906 "
        "src: /10.250.19.102:54106 "
        "dest: /10.250.19.102:50010"
    )

    result = run_diagnosis(log_line=log_line, top_k=3)

    assert result["status"] in {
        "anomaly_flagged",
        "no_anomaly_flagged",
    }
    assert isinstance(result["assessment"], str)
    assert isinstance(result["incident_assessment"], dict)
    assert "recommendations" in result["incident_assessment"]
    assert "limitations" in result["incident_assessment"]
    assert "root_cause" in result["incident_assessment"]
