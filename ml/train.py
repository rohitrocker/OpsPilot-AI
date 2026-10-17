
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = PROJECT_ROOT / "ml" / "data" / "log_features.csv"
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"

MODEL_FILE = ARTIFACT_DIR / "anomaly_model.joblib"
METADATA_FILE = ARTIFACT_DIR / "model_metadata.json"

# Maximum number of rows used for this baseline model.
MAX_TRAIN_ROWS = 100_000
RANDOM_STATE = 42


def train_model():
    """Train and save an unsupervised log anomaly detector."""

    # --------------------------------------------------
    # 2. Validate input
    # --------------------------------------------------

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {DATA_FILE}\n"
            "Run ml/features.py first."
        )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # 3. Read a bounded sample of the dataset
    # --------------------------------------------------

    print("Loading a sample of feature data...")

    data = pd.read_csv(
        DATA_FILE,
        nrows=MAX_TRAIN_ROWS,
    )

    if data.empty:
        raise ValueError("The feature dataset contains no rows.")

    # Use numeric indicators and message statistics.
    # Raw message text, dates, PIDs and component names
    # are not passed directly to this baseline model.
    feature_columns = [
        "message_length",
        "token_count",
        "digit_count",
        "has_error_keyword",
        "has_block_id",
        "has_ip_address",
    ]

    missing_columns = [
        column for column in feature_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required features: {missing_columns}"
        )

    X = data[feature_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    # Replace invalid values and remove infinite values.
    X = X.replace([float("inf"), float("-inf")], float("nan"))
    X = X.fillna(0)

    # Remove duplicate feature rows to reduce redundant samples.
    X = X.drop_duplicates()

    if len(X) < 2:
        raise ValueError(
            "Not enough distinct feature rows to train."
        )

    print(f"Rows loaded: {len(data):,}")
    print(f"Distinct rows used: {len(X):,}")
    print(f"Features: {feature_columns}")

    # --------------------------------------------------
    # 4. Build the anomaly detection pipeline
    # --------------------------------------------------

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "detector",
                IsolationForest(
                    n_estimators=100,
                    contamination="auto",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    # --------------------------------------------------
    # 5. Train the model
    # --------------------------------------------------

    print("\nTraining Isolation Forest...")
    model.fit(X)

    # --------------------------------------------------
    # 6. Inspect predictions on the training sample
    # --------------------------------------------------

    predictions = model.predict(X)

    # Isolation Forest returns:
    #  1  = inlier (not flagged)
    # -1  = outlier (flagged as anomalous)
    flagged = int((predictions == -1).sum())
    normal = int((predictions == 1).sum())

    print("\nTraining sample results")
    print(f"Not flagged: {normal:,}")
    print(f"Flagged as anomalous: {flagged:,}")
    print(
        "Flagged percentage: "
        f"{flagged / len(X) * 100:.2f}%"
    )

    # --------------------------------------------------
    # 7. Save model and metadata
    # --------------------------------------------------

    joblib.dump(model, MODEL_FILE)

    metadata = {
        "model_type": "IsolationForest",
        "feature_columns": feature_columns,
        "training_rows_loaded": int(len(data)),
        "distinct_rows_used": int(len(X)),
        "random_state": RANDOM_STATE,
        "contamination": "auto",
        "label_status": "unlabeled_unsupervised_baseline",
    }

    METADATA_FILE.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8",
    )

    print("\nTraining complete!")
    print(f"Model saved to: {MODEL_FILE}")
    print(f"Metadata saved to: {METADATA_FILE}")
    print(
        "\nNote: flagged records are candidates for investigation, "
        "not confirmed incidents."
    )


if __name__ == "__main__":
    train_model()

