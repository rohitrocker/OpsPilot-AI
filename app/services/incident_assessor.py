


from typing import Any


def assess_incident(
    incident: dict[str, Any],
    prediction: dict[str, Any],
    runbooks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a cautious, evidence-based incident assessment."""

    is_anomaly = prediction.get("is_anomaly", False)

    if is_anomaly:
        status = "anomaly_flagged"
        summary = (
            "The anomaly detection model flagged this log record "
            "as unusual. Further investigation is required."
        )
    else:
        status = "no_anomaly_flagged"
        summary = (
            "The model did not flag this log record as unusual. "
            "This does not guarantee that the system is healthy."
        )

    component = incident.get("component", "Unknown")
    level = incident.get("level", "Unknown")
    message = incident.get("message", "")

    recommendations = []

    if level.upper() in {"ERROR", "FATAL", "CRITICAL"}:
        recommendations.append(
            "Inspect the surrounding logs and identify the operation "
            "that failed."
        )

    if is_anomaly:
        recommendations.append(
            "Compare this record with nearby logs and known normal "
            "behavior before determining a root cause."
        )

    if runbooks:
        recommendations.append(
            "Review the retrieved runbooks and confirm that their "
            "guidance applies to this specific event."
        )
    else:
        recommendations.append(
            "No matching runbook evidence was retrieved. "
            "Consult the relevant system documentation."
        )

    return {
        "status": status,
        "summary": summary,
        "component": component,
        "log_level": level,
        "observed_message": message,
        "anomaly_score": prediction.get("anomaly_score"),
        "matching_runbooks": len(runbooks),
        "root_cause": None,
        "recommendations": recommendations,
        "limitations": [
            "An anomaly flag is not proof of a real incident.",
            "The assessment does not establish a root cause.",
            "Recommendations require verification against system evidence.",
        ],
    }
