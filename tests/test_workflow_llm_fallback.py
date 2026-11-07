
from unittest.mock import patch

from app.agents.workflow import run_diagnosis


def test_llm_failure_does_not_stop_diagnosis():
    log_line = (
        "081109 203518 143 INFO "
        "dfs.DataNode$DataXceiver: Receiving block "
        "blk_-1608999687919862906 "
        "src: /10.250.19.102:54106 "
        "dest: /10.250.19.102:50010"
    )

    with patch(
        "app.agents.workflow.explain_incident",
        side_effect=RuntimeError("Simulated Groq failure"),
    ):
        result = run_diagnosis(log_line=log_line, top_k=3)

    assert result["llm_status"] == "unavailable"
    assert result["llm_explanation"] is None
    assert result["llm_error"] is not None
    assert "analysis" in result
    assert "incident_assessment" in result
