
"""Validate runbook documents and create a knowledge-base manifest."""

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_DIR = PROJECT_ROOT / "knowledge_base" / "runbooks"
MANIFEST_PATH = PROJECT_ROOT / "knowledge_base" / "manifest.json"

SUPPORTED_EXTENSIONS = {".md", ".txt"}
MIN_CONTENT_LENGTH = 20


def discover_runbooks() -> list[Path]:
    """Find supported runbook files, including files in subdirectories."""
    if not RUNBOOK_DIR.is_dir():
        raise FileNotFoundError(
            f"Runbook directory does not exist: {RUNBOOK_DIR}"
        )

    return sorted(
        path
        for path in RUNBOOK_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def inspect_runbook(path: Path) -> dict[str, object]:
    """Read one document and report whether it is suitable for ingestion."""
    relative_path = str(path.relative_to(RUNBOOK_DIR))

    try:
        content = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        return {
            "source": relative_path,
            "status": "error",
            "reason": f"Could not read document: {exc}",
        }

    if not content:
        return {
            "source": relative_path,
            "status": "skipped",
            "reason": "Document is empty.",
        }

    if len(content) < MIN_CONTENT_LENGTH:
        return {
            "source": relative_path,
            "status": "warning",
            "reason": "Document is very short; review its content.",
            "character_count": len(content),
        }

    title = path.stem.replace("_", " ").replace("-", " ").strip()

    return {
        "source": relative_path,
        "title": title,
        "status": "ready",
        "character_count": len(content),
        "word_count": len(content.split()),
    }


def build_manifest() -> dict[str, object]:
    """Inspect the available runbooks and summarize their status."""
    paths = discover_runbooks()
    documents = [inspect_runbook(path) for path in paths]

    ready_count = sum(
        document["status"] == "ready" for document in documents
    )
    warning_count = sum(
        document["status"] == "warning" for document in documents
    )
    skipped_count = sum(
        document["status"] == "skipped" for document in documents
    )
    error_count = sum(
        document["status"] == "error" for document in documents
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runbook_directory": str(RUNBOOK_DIR),
        "summary": {
            "total_documents": len(documents),
            "ready": ready_count,
            "warnings": warning_count,
            "skipped": skipped_count,
            "errors": error_count,
        },
        "documents": documents,
    }


def main() -> None:
    """Run ingestion validation and save the manifest."""
    manifest = build_manifest()

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = MANIFEST_PATH.with_suffix(".tmp")

    try:
        temporary_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(MANIFEST_PATH)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    summary = manifest["summary"]

    print("Knowledge-base ingestion check complete.")
    print(f"Runbooks discovered: {summary['total_documents']}")
    print(f"Ready: {summary['ready']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")
    print(f"Manifest saved to: {MANIFEST_PATH}")

    if summary["errors"]:
        print("Some documents could not be read. Review the manifest.")


if __name__ == "__main__":
    main()
