
from pathlib import Path
import json

import joblib
import pandas as pd

# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "ml" / "data" / "log_features.csv"
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"

MODEL_FILE = ARTIFACT_DIR / "anomaly_model.joblib"
METADATA_FILE = ARTIFACT_DIR / "model_metadata.json"

OUTPUT_FILE = PROJECT_ROOT / "ml" / "data" / "flagged_anomalies.csv"
REPORT_FILE = ARTIFACT_DIR / "evaluation_report.json"

CHUNK_SIZE = 50_000


def evaluate_model():
    # --------------------------------------------------
    # 2. Check required files
    # --------------------------------------------------

    for file_path in [DATA_FILE, MODEL_FILE, METADATA_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path}\n"
                "Complete feature extraction and training first."
            )

    print("Loading trained model...")

    model = joblib.load(MODEL_FILE)
    metadata = json.loads(
        METADATA_FILE.read_text(encoding="utf-8")
    )
    feature_columns = metadata["feature_columns"]

    # Start a fresh report for this evaluation run.
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_rows = 0
    flagged_rows = 0
    score_sum = 0.0
    lowest_score = float("inf")
    highest_score = float("-inf")
    output_created = False

    print("Evaluating feature data in chunks...")

    # --------------------------------------------------
    # 3. Process the large CSV without loading it all
    # --------------------------------------------------

    for chunk_number, chunk in enumerate(
        pd.read_csv(DATA_FILE, chunksize=CHUNK_SIZE),
        start=1,
    ):
        missing = [
            column for column in feature_columns
            if column not in chunk.columns
        ]

        if missing:
            raise ValueError(f"Missing features: {missing}")

        X = chunk[feature_columns].apply(
            pd.to_numeric, errors="coerce"
        )
        X = X.replace([float("inf"), float("-inf")], float("nan"))
        X = X.fillna(0)

        # Isolation Forest:
        # predict() returns -1 for flagged outliers and 1 otherwise.
        predictions = model.predict(X)

        # Lower decision_function values are more anomalous.
        # Negating them makes higher scores more anomalous.
        anomaly_scores = -model.decision_function(X)

        chunk["anomaly_score"] = anomaly_scores
        chunk["anomaly_prediction"] = predictions
        chunk["is_anomaly"] = (predictions == -1)

        flagged = chunk[chunk["is_anomaly"]].copy()

        if not flagged.empty:
            flagged.to_csv(
                OUTPUT_FILE,
                mode="a",
                index=False,
                header=not output_created,
            )
            output_created = True
            flagged_rows += len(flagged)

        total_rows += len(chunk)
        score_sum += float(anomaly_scores.sum())
        lowest_score = min(lowest_score, float(anomaly_scores.min()))
        highest_score = max(highest_score, float(anomaly_scores.max()))

        print(
            f"Chunk {chunk_number}: "
            f"{total_rows:,} rows checked, "
            f"{flagged_rows:,} flagged"
        )

    # --------------------------------------------------
    # 4. Create evaluation report
    # --------------------------------------------------

    report = {
        "model_type": metadata["model_type"],
        "evaluation_rows": total_rows,
        "flagged_rows": flagged_rows,
        "not_flagged_rows": total_rows - flagged_rows,
        "flagged_percentage": (
            round(flagged_rows / total_rows * 100, 3)
            if total_rows else 0
        ),
        "mean_anomaly_score": (
            round(score_sum / total_rows, 6)
            if total_rows else None
        ),
        "minimum_anomaly_score": (
            round(lowest_score, 6) if total_rows else None
        ),
        "maximum_anomaly_score": (
            round(highest_score, 6) if total_rows else None
        ),
        "ground_truth_labels_available": False,
        "note": (
            "These are model-flagged candidates, not confirmed incidents. "
            "Accuracy, precision, recall and F1 require ground-truth labels."
        ),
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    print("\n========== EVALUATION REPORT ==========")
    print(json.dumps(report, indent=4))
    print(f"\nFlagged records: {OUTPUT_FILE}")
    print(f"Report saved: {REPORT_FILE}")


if __name__ == "__main__":
    evaluate_model()
