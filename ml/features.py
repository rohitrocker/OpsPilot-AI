
from pathlib import Path
import csv
import re
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "ml" / "data" / "parsed_hdfs_logs.csv"
OUTPUT_FILE = PROJECT_ROOT / "ml" / "data" / "log_features.csv"

ERROR_PATTERN = re.compile(
    r"\b(error|exception|failed|failure|fatal|timeout|denied)\b",
    re.IGNORECASE,
)
BLOCK_PATTERN = re.compile(r"\bblk_-?\d+\b", re.IGNORECASE)
IP_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)
NUMBER_PATTERN = re.compile(r"\d+")
TOKEN_PATTERN = re.compile(r"\b[\w$.-]+\b")


def extract_features():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {INPUT_FILE}\n"
            "Run ml/preprocess.py first."
        )

    total_rows = 0
    level_counts = Counter()

    print(f"Input: {INPUT_FILE}")
    print("Extracting features in streaming mode...")

    with INPUT_FILE.open(
        "r", encoding="utf-8", newline=""
    ) as source, OUTPUT_FILE.open(
        "w", encoding="utf-8", newline=""
    ) as destination:

        reader = csv.DictReader(source)

        required = {
            "date", "time", "pid", "level", "component", "message"
        }
        if not reader.fieldnames or not required.issubset(
            set(reader.fieldnames)
        ):
            raise ValueError(
                "CSV must contain date, time, pid, level, "
                "component, and message columns."
            )

        fields = [
            "date",
            "time",
            "pid",
            "level",
            "component",
            "message_length",
            "token_count",
            "digit_count",
            "has_error_keyword",
            "has_block_id",
            "has_ip_address",
        ]

        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()

        for row in reader:
            message = row.get("message") or ""
            level = (row.get("level") or "").upper()

            writer.writerow({
                "date": row.get("date", ""),
                "time": row.get("time", ""),
                "pid": row.get("pid", ""),
                "level": level,
                "component": row.get("component", ""),
                "message_length": len(message),
                "token_count": len(TOKEN_PATTERN.findall(message)),
                "digit_count": len(NUMBER_PATTERN.findall(message)),
                "has_error_keyword": int(
                    bool(ERROR_PATTERN.search(message))
                ),
                "has_block_id": int(
                    bool(BLOCK_PATTERN.search(message))
                ),
                "has_ip_address": int(
                    bool(IP_PATTERN.search(message))
                ),
            })

            level_counts[level or "UNKNOWN"] += 1
            total_rows += 1

            if total_rows % 100_000 == 0:
                print(f"Processed {total_rows:,} rows...")

    print("\nFeature extraction complete!")
    print(f"Rows processed: {total_rows:,}")
    print(f"Log level counts: {dict(level_counts)}")
    print(f"Features saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    extract_features()
