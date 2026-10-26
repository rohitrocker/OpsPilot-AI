
"""Reusable tools for the OpsPilot AI incident diagnosis agent."""

from typing import Any

from app.services.classifier import AnomalyClassifier
from app.services.log_parser import prepare_log_for_prediction
from app.services.rag_service import retrieve_runbooks


def analyze_log_record(
    log_line: str,
    classifier: AnomalyClassifier | None = None,
) -> dict[str, Any]:
    """Parse a raw log line, extract features, and predict anomalies."""
    if not isinstance(log_line, str):
        raise TypeError("log_line must be a string.")

    if not log_line.strip():
        raise ValueError("log_line cannot be empty.")

    prepared = prepare_log_for_prediction(log_line)

    # Allow dependency injection so tests can supply a classifier.
    active_classifier = classifier or AnomalyClassifier()
    prediction = active_classifier.predict_one(prepared["features"])

    return {
        "parsed_log": prepared["parsed_log"],
        "features": prepared["features"],
        "prediction": prediction,
    }


def find_troubleshooting_guidance(
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Retrieve runbooks relevant to an incident or log message."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    runbooks = retrieve_runbooks(query, top_k=top_k)

    return {
        "query": query,
        "results_count": len(runbooks),
        "runbooks": runbooks,
        "message": (
            "Relevant runbooks found."
            if runbooks
            else "No matching runbooks found. Do not assume a root cause."
        ),
    }


def diagnose_log(
    log_line: str,
    classifier: AnomalyClassifier | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """Combine anomaly prediction with relevant troubleshooting evidence."""
    analysis = analyze_log_record(log_line, classifier=classifier)

    parsed_log = analysis["parsed_log"]
    prediction = analysis["prediction"]

    # Use the log text and parsed component to search for useful guidance.
    query = (
        f"{parsed_log['component']} "
        f"{parsed_log['level']} "
        f"{parsed_log['message']}"
    )

    guidance = find_troubleshooting_guidance(query, top_k=top_k)

    return {
        "incident": {
            "component": parsed_log["component"],
            "level": parsed_log["level"],
            "message": parsed_log["message"],
        },
        "analysis": analysis,
        "troubleshooting": guidance,
        "assessment": (
            "The model flagged this record as anomalous."
            if prediction["is_anomaly"]
            else "The model did not flag this record as anomalous."
        ),
        "limitations": [
            "An anomaly prediction does not prove an incident occurred.",
            "Retrieved runbooks are supporting evidence, not confirmed root causes.",
            "Keyword-based retrieval may miss relevant documents.",
        ],
    }
