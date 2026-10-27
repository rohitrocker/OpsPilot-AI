
from typing import Any

from app.agents.tools import diagnose_log
from app.services.incident_assessor import assess_incident
from app.services.llm_explainer import explain_incident


class IncidentWorkflow:
    """Coordinate anomaly detection, runbook retrieval, and explanation."""

    def __init__(self, top_k: int = 3) -> None:
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise ValueError("top_k must be an integer.")

        if not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10.")

        self.top_k = top_k

    def run(self, log_line: str) -> dict[str, Any]:
        if not isinstance(log_line, str):
            raise TypeError("log_line must be a string.")

        if not log_line.strip():
            raise ValueError("log_line cannot be empty.")

        # 1. Parse the log, predict anomalies, and retrieve runbooks.
        result = diagnose_log(
            log_line=log_line,
            top_k=self.top_k,
        )

        prediction = result["analysis"]["prediction"]
        runbooks = result["troubleshooting"]["runbooks"]

        # 2. Generate the rule-based assessment.
        incident_assessment = assess_incident(
            incident=result["incident"],
            prediction=prediction,
            runbooks=runbooks,
        )

        # 3. Generate an LLM explanation without breaking diagnosis
        #    if the external LLM service is unavailable.
        try:
            llm_explanation = explain_incident(
                incident=result["incident"],
                prediction=prediction,
                runbooks=runbooks,
            )
            llm_status = "success"
            llm_error = None

        except Exception:
            llm_explanation = None
            llm_status = "unavailable"
            llm_error = (
                "The AI explanation could not be generated. "
                "Use the rule-based assessment and troubleshooting results."
            )

        # 4. Return the complete diagnosis.
        return {
            "status": incident_assessment["status"],
            "incident": result["incident"],
            "analysis": result["analysis"],
            "troubleshooting": result["troubleshooting"],
            "assessment": incident_assessment["summary"],
            "incident_assessment": incident_assessment,
            "llm_explanation": llm_explanation,
            "llm_status": llm_status,
            "llm_error": llm_error,
            "evidence_available": bool(runbooks),
            "limitations": incident_assessment["limitations"],
        }


def run_diagnosis(
    log_line: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Run the complete incident diagnosis workflow."""
    return IncidentWorkflow(top_k=top_k).run(log_line)
