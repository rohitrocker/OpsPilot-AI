
"""Coordinate the OpsPilot AI incident diagnosis workflow."""

from typing import Any

from app.agents.tools import diagnose_log


class IncidentWorkflow:
    """Run log analysis and gather supporting troubleshooting evidence."""

    def __init__(self, top_k: int = 3) -> None:
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        self.top_k = top_k

    def run(self, log_line: str) -> dict[str, Any]:
        """Analyze one log line and return a structured diagnosis report."""
        if not isinstance(log_line, str):
            raise TypeError("log_line must be a string.")

        if not log_line.strip():
            raise ValueError("log_line cannot be empty.")

        # Delegate the actual prediction and retrieval to reusable tools.
        result = diagnose_log(
            log_line=log_line,
            top_k=self.top_k,
        )

        prediction = result["analysis"]["prediction"]
        runbooks = result["troubleshooting"]["runbooks"]

        # Keep model predictions separate from evidence-based conclusions.
        if prediction["is_anomaly"]:
            status = "anomaly_flagged"
        else:
            status = "no_anomaly_flagged"

        return {
            "status": status,
            "incident": result["incident"],
            "analysis": result["analysis"],
            "troubleshooting": result["troubleshooting"],
            "assessment": result["assessment"],
            "evidence_available": bool(runbooks),
            "limitations": result["limitations"],
        }


def run_diagnosis(log_line: str, top_k: int = 3) -> dict[str, Any]:
    """Convenience entry point for running a diagnosis."""
    workflow = IncidentWorkflow(top_k=top_k)
    return workflow.run(log_line)
