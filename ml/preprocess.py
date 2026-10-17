
from pathlib import Path
import csv
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "ml" / "data" / "sorted.log"
OUTPUT_FILE = PROJECT_ROOT / "ml" / "data" / "parsed_hdfs_logs.csv"

LOG_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<pid>\d+)\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG|FATAL)\s+"
    r"(?P<component>[^:]+):\s*"
    r"(?P<message>.*)$"
)


def preprocess_logs():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    total_lines = 0
    parsed_lines = 0
    malformed_lines = 0

    print(f"Reading: {INPUT_FILE}")
    print("Starting preprocessing...")

    with INPUT_FILE.open(
        "r", encoding="utf-8", errors="replace"
    ) as source, OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as destination:

        writer = csv.DictWriter(
            destination,
            fieldnames=[
                "date", "time", "pid",
                "level", "component", "message"
            ],
        )
        writer.writeheader()

        for line in source:
            total_lines += 1
            line = line.strip()

            if not line:
                continue

            match = LOG_PATTERN.match(line)

            if match:
                writer.writerow(match.groupdict())
                parsed_lines += 1
            else:
                malformed_lines += 1

            if total_lines % 100_000 == 0:
                print(
                    f"Processed {total_lines:,} lines | "
                    f"Parsed {parsed_lines:,}"
                )

    print("\nPreprocessing finished!")
    print(f"Total lines: {total_lines:,}")
    print(f"Parsed lines: {parsed_lines:,}")
    print(f"Unmatched lines: {malformed_lines:,}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    preprocess_logs()
