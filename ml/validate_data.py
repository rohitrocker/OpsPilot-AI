
from pathlib import Path
import csv
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "ml" / "data" / "parsed_hdfs_logs.csv"


def validate_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"CSV not found: {INPUT_FILE}\n"
            "Run ml/preprocess.py first."
        )

    required_columns = {
        "date", "time", "pid", "level", "component", "message"
    }

    total_rows = 0
    empty_messages = 0
    levels = Counter()
    components = Counter()
    samples = []

    print(f"Reading dataset: {INPUT_FILE}")
    print("Validating CSV in streaming mode...\n")

    with INPUT_FILE.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("The CSV has no header.")

        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        for row in reader:
            total_rows += 1

            level = (row.get("level") or "").strip()
            component = (row.get("component") or "").strip()
            message = (row.get("message") or "").strip()

            levels[level or "EMPTY"] += 1
            components[component or "EMPTY"] += 1

            if not message:
                empty_messages += 1

            if len(samples) < 5:
                samples.append(row)

            if total_rows % 100_000 == 0:
                print(f"Validated {total_rows:,} rows...")

    print("\n========== VALIDATION REPORT ==========")
    print(f"Total rows: {total_rows:,}")
    print(f"Empty messages: {empty_messages:,}")
    print(f"Unique components: {len(components):,}")

    print("\nLog levels:")
    for level, count in levels.most_common():
        print(f"  {level}: {count:,}")

    print("\nTop 10 components:")
    for component, count in components.most_common(10):
        print(f"  {component}: {count:,}")

    print("\nSample records:")
    for record in samples:
        print(record)

    print("\nValidation completed.")


if __name__ == "__main__":
    validate_data()
