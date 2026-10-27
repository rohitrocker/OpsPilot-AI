
"""Pydantic schemas for incident analysis and diagnosis requests."""

from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict


class IncidentFeatures(BaseModel):
    """Numerical features already extracted from a log record."""

    model_config = ConfigDict(extra="forbid")

    message_length: float = Field(ge=0)
    token_count: float = Field(ge=0)
    digit_count: float = Field(ge=0)
    has_error_keyword: float = Field(ge=0, le=1)
    has_block_id: float = Field(ge=0, le=1)
    has_ip_address: float = Field(ge=0, le=1)


class RawLogRequest(BaseModel):
    """Raw log text submitted for analysis."""

    model_config = ConfigDict(extra="forbid")

    log_line: str = Field(min_length=1, max_length=10_000)


class DiagnosisRequest(RawLogRequest):
    """Request for end-to-end diagnosis with runbook retrieval."""

    top_k: int = Field(default=3, ge=1, le=10)


class IncidentPrediction(BaseModel):
    """Prediction returned by the anomaly detection model."""

    is_anomaly: bool
    prediction: Literal["anomaly", "normal"]
    anomaly_score: float
    score_note: str


class LogAnalysisResponse(IncidentPrediction):
    """Prediction plus parsed log details and extracted features."""

    parsed_log: dict[str, Any]
    features: dict[str, int]



class DiagnosisResponse(BaseModel):
    status: Literal["anomaly_flagged", "no_anomaly_flagged"]
    incident: dict[str, str]
    analysis: dict[str, Any]
    troubleshooting: dict[str, Any]
    assessment: str
    incident_assessment: dict[str, Any]
    evidence_available: bool
    limitations: list[str]

