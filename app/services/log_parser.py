
"""Parse HDFS log lines and extract model-ready numerical features."""

import re
from typing import Any


# Example:
# 081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block ...
HDFS_LOG_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<pid>\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<component>[^:]+):\s*"
    r"(?P<message>.*)$"
)

BLOCK_ID_PATTERN = re.compile(r"\bblk_-?\d+\b")
IP_ADDRESS_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

ERROR_KEYWORDS = (
    "error",
    "exception",
    "failed",
    "failure",
    "fatal",
)


def parse_log_line(log_line: str) -> dict[str, Any]:
    """Parse one HDFS log line into structured fields."""
    if not isinstance(log_line, str):
        raise TypeError("log_line must be a string.")

    log_line = log_line.strip()
    if not log_line:
        raise ValueError("log_line cannot be empty.")

    match = HDFS_LOG_PATTERN.match(log_line)
    if not match:
        raise ValueError(
            "Log line does not match the expected HDFS log format."
        )

    record = match.groupdict()

    return {
        "date": record["date"],
        "time": record["time"],
        "pid": int(record["pid"]),
        "level": record["level"],
        "component": record["component"].strip(),
        "message": record["message"].strip(),
    }


def extract_features(parsed_log: dict[str, Any]) -> dict[str, int]:
    """Convert a parsed log record into the six model input features."""
    message = parsed_log.get("message")

    if not isinstance(message, str):
        raise ValueError("Parsed log must contain a string 'message'.")

    normalized_message = message.lower()

    has_error_keyword = any(
        keyword in normalized_message
        for keyword in ERROR_KEYWORDS
    )

    return {
        "message_length": len(message),
        "token_count": len(message.split()),
        "digit_count": sum(character.isdigit() for character in message),
        "has_error_keyword": int(has_error_keyword),
        "has_block_id": int(bool(BLOCK_ID_PATTERN.search(message))),
        "has_ip_address": int(bool(IP_ADDRESS_PATTERN.search(message))),
    }


def prepare_log_for_prediction(log_line: str) -> dict[str, Any]:
    """Parse a raw log line and return its fields and numerical features."""
    parsed_log = parse_log_line(log_line)
    features = extract_features(parsed_log)

    return {
        "parsed_log": parsed_log,
        "features": features,
    }
