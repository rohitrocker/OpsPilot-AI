
"""Reusable service for predicting anomalies in HDFS log features."""

import json
import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "artifacts" / "anomaly_model.joblib"
METADATA_PATH = PROJECT_ROOT / "ml" / "artifacts" / "model_metadata.json"


class AnomalyClassifier:
    """Load the trained model and classify prepared log features."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        metadata_path: Path = METADATA_PATH,
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)

        self._check_artifacts()

        # Load the model once, rather than on every prediction.
        self.model = joblib.load(self.model_path)

        with self.metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)

        self.feature_columns = metadata.get("feature_columns")
        if not isinstance(self.feature_columns, list) or not self.feature_columns:
            raise ValueError(
                "Model metadata must contain a non-empty 'feature_columns' list."
            )

    def _check_artifacts(self) -> None:
        """Fail early with a useful message if training artifacts are missing."""
        missing_files = [
            path for path in (self.model_path, self.metadata_path)
            if not path.is_file()
        ]

        if missing_files:
            paths = ", ".join(str(path) for path in missing_files)
            raise FileNotFoundError(
                f"Required model artifact(s) not found: {paths}. "
                "Run ml/train.py first."
            )

    def _prepare_features(self, features: dict[str, Any]) -> pd.DataFrame:
        """Validate input and arrange features in the model's expected order."""
        if not isinstance(features, dict):
            raise TypeError("features must be a dictionary.")

        missing = [
            name for name in self.feature_columns
            if name not in features
        ]
        if missing:
            raise ValueError(f"Missing required feature(s): {missing}")

        values: dict[str, float] = {}

        for name in self.feature_columns:
            value = features[name]

            # Reject strings, None, and booleans instead of silently
            # converting potentially incorrect input into numeric features.
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"Feature '{name}' must be a numeric value; got {value!r}."
                )

            numeric_value = float(value)
            if not math.isfinite(numeric_value):
                raise ValueError(
                    f"Feature '{name}' must be finite; got {value!r}."
                )

            values[name] = numeric_value

        # A DataFrame preserves feature names and the exact training order.
        return pd.DataFrame([values], columns=self.feature_columns)

    def predict_one(self, features: dict[str, Any]) -> dict[str, Any]:
        """Classify one already-prepared log record."""
        row = self._prepare_features(features)

        prediction = int(self.model.predict(row)[0])
        anomaly_score = float(-self.model.decision_function(row)[0])

        return {
            "is_anomaly": prediction == -1,
            "prediction": "anomaly" if prediction == -1 else "normal",
            "anomaly_score": anomaly_score,
            "score_note": "Higher scores indicate more unusual records.",
        }

    def predict_many(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Classify multiple records using the same validation rules."""
        if not isinstance(records, list):
            raise TypeError("records must be a list of feature dictionaries.")

        return [self.predict_one(record) for record in records]
