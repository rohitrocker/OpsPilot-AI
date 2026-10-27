
from typing import Any

from app.agents.tools import diagnose_log
from app.services.incident_assessor import assess_incident


class IncidentWorkflow:
    """Coordinate log diagnosis and incident assessment."""

    def __init__(self, top_k: int = 3) -> None:
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise ValueError("top_k must be an integer.")

        if top_k < 1 or top_k > 10:
            raise ValueError("top_k must be between 1 and 10.")

        self.top_k = top_k

    def run(self, log_line: str) -> dict[str, Any]:
        if not isinstance(log_line, str):
            raise TypeError("log_line must be a string.")

        if not log_line.strip():
            raise ValueError("log_line cannot be empty.")

        # Step 1: Parse the log, predict anomalies, and retrieve runbooks.
        result = diagnose_log(
            log_line=log_line,
            top_k=self.top_k,
        )

        prediction = result["analysis"]["prediction"]
        runbooks = result["troubleshooting"]["runbooks"]

        # Step 2: Build a structured incident assessment.
        incident_assessment = assess_incident(
            incident=result["incident"],
            prediction=prediction,
            runbooks=runbooks,
        )

        # Step 3: Return the combined diagnosis.
        return {
            "status": incident_assessment["status"],
            "incident": result["incident"],
            "analysis": result["analysis"],
            "troubleshooting": result["troubleshooting"],
            "assessment": incident_assessment["summary"],
            "incident_assessment": incident_assessment,
            "evidence_available": bool(runbooks),
            "limitations": incident_assessment["limitations"],
        }


def run_diagnosis(
    log_line: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Run the complete incident diagnosis workflow."""
    workflow = IncidentWorkflow(top_k=top_k)
    return workflow.run(log_line)
