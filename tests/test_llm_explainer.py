
from types import SimpleNamespace

import pytest

import app.services.llm_explainer as explainer


class FakeChatGroq:
    """Simulate Groq without making a network request."""

    def __init__(self, **kwargs):
        self.config = kwargs

    def invoke(self, messages):
        return SimpleNamespace(
            content=(
                "Observations: The log reports a block replication failure.\n"
                "Interpretation: Further investigation is needed.\n"
                "Supporting Evidence: The supplied log message.\n"
                "Recommended Checks: Inspect DataNode health and nearby logs.\n"
                "Uncertainty: The root cause is not confirmed."
            )
        )


def test_explain_incident_returns_text(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv(
        "GROQ_MODEL_NAME",
        "test-model",
    )
    monkeypatch.setattr(
        explainer,
        "ChatGroq",
        FakeChatGroq,
    )

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

    runbooks = [
        {
            "title": "HDFS Block Troubleshooting",
            "content": (
                "Check DataNode health, replication status, "
                "and relevant surrounding logs."
            ),
        }
    ]

    explanation = explainer.explain_incident(
        incident=incident,
        prediction=prediction,
        runbooks=runbooks,
    )

    assert isinstance(explanation, str)
    assert "Observations:" in explanation
    assert "Uncertainty:" in explanation


def test_explain_incident_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is missing",
    ):
        explainer.explain_incident(
            incident={},
            prediction={},
            runbooks=[],
        )

