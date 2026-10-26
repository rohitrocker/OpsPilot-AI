
"""API endpoints for HDFS log analysis and anomaly detection."""

from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.schemas.incident import DiagnosisRequest, DiagnosisResponse
from app.services.classifier import AnomalyClassifier
from app.services.log_parser import prepare_log_for_prediction
from app.agents.workflow import run_diagnosis
from app.schemas.incident import (
    DiagnosisRequest,
    DiagnosisResponse,
    IncidentFeatures,
    IncidentPrediction,
    LogAnalysisResponse,
    RawLogRequest,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])



class IncidentFeatures(BaseModel):
    """Numerical features already extracted from a log record."""

    message_length: float = Field(ge=0)
    token_count: float = Field(ge=0)
    digit_count: float = Field(ge=0)
    has_error_keyword: float = Field(ge=0, le=1)
    has_block_id: float = Field(ge=0, le=1)
    has_ip_address: float = Field(ge=0, le=1)


class RawLogRequest(BaseModel):
    """Raw log text submitted for analysis."""

    log_line: str = Field(min_length=1, max_length=10_000)


class IncidentPrediction(BaseModel):
    """Prediction returned by the anomaly detection model."""

    is_anomaly: bool
    prediction: str
    anomaly_score: float
    score_note: str


class LogAnalysisResponse(IncidentPrediction):
    """Prediction together with parsed log data and extracted features."""

    parsed_log: dict[str, Any]
    features: dict[str, int]


class DiagnosisRequest(BaseModel):
    """Raw log submitted for end-to-end incident diagnosis."""

    log_line: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=3, ge=1, le=10)



@router.post(
    "/diagnose",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_200_OK,
)
def diagnose_incident(
    request: DiagnosisRequest,
) -> dict[str, Any]:
    """Run the full anomaly detection and runbook retrieval workflow."""
    try:
        return run_diagnosis(
            log_line=request.log_line,
            top_k=request.top_k,
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Required model or knowledge-base files are unavailable.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during diagnosis.",
        ) from exc

@lru_cache(maxsize=1)
def get_classifier() -> AnomalyClassifier:
    """Reuse one classifier instance across requests."""
    return AnomalyClassifier()


@router.get("/health")
def incidents_health() -> dict[str, str]:
    """Check whether the incident router is responding."""
    return {"status": "ok", "service": "incident-detection"}


@router.post(
    "/predict",
    response_model=IncidentPrediction,
    status_code=status.HTTP_200_OK,
)
def predict_incident(
    features: IncidentFeatures,
) -> IncidentPrediction:
    """Predict using numerical features supplied by the caller."""
    try:
        result = get_classifier().predict_one(features.model_dump())
        return IncidentPrediction(**result)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifacts are missing. Train the model first.",
        ) from exc

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during prediction.",
        ) from exc


@router.post(
    "/analyze",
    response_model=LogAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_log(request: RawLogRequest) -> LogAnalysisResponse:
    """Parse raw HDFS log text and predict whether it looks anomalous."""
    try:
        # Step 1: Convert raw text into structured data and model features.
        prepared = prepare_log_for_prediction(request.log_line)

        parsed_log = prepared["parsed_log"]
        features = prepared["features"]

        # Step 2: Ask the trained model to classify those features.
        prediction = get_classifier().predict_one(features)

        # Step 3: Return the prediction alongside the extracted data.
        return LogAnalysisResponse(
            **prediction,
            parsed_log=parsed_log,
            features=features,
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifacts are missing. Train the model first.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during log analysis.",
        ) from exc
