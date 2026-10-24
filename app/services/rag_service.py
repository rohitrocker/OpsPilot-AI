
"""Retrieve relevant troubleshooting runbooks for an incident."""

import re
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNBOOK_DIR = PROJECT_ROOT / "knowledge_base" / "runbooks"

SUPPORTED_EXTENSIONS = {".md", ".txt"}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "in", "is", "it", "of", "on", "or", "the", "to",
    "was", "were", "with", "this", "that", "if", "when",
}


@dataclass(frozen=True)
class Runbook:
    """A troubleshooting document loaded from disk."""

    title: str
    source: str
    content: str
    terms: frozenset[str]


class RunbookRetriever:
    """Search local runbooks using lightweight keyword matching."""

    def __init__(self, runbook_dir: Path = RUNBOOK_DIR) -> None:
        self.runbook_dir = Path(runbook_dir)
        self._runbooks: list[Runbook] = []
        self.reload()

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Normalize text into searchable terms."""
        words = re.findall(r"[a-zA-Z0-9_-]+", text.lower())
        return {word for word in words if word not in STOPWORDS}

    def reload(self) -> int:
        """Load supported runbook files and return the number loaded."""
        self._runbooks = []

        if not self.runbook_dir.is_dir():
            return 0

        for path in sorted(self.runbook_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            try:
                content = path.read_text(encoding="utf-8").strip()
            except (OSError, UnicodeError):
                # Skip files that cannot be read safely as text.
                continue

            if not content:
                continue

            title = path.stem.replace("_", " ").replace("-", " ").strip()

            self._runbooks.append(
                Runbook(
                    title=title,
                    source=str(path.relative_to(self.runbook_dir)),
                    content=content,
                    terms=frozenset(self._tokenize(content)),
                )
            )

        return len(self._runbooks)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, object]]:
        """Return runbooks ranked by keyword overlap with the query."""
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        if not query.strip():
            raise ValueError("query cannot be empty.")

        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        results: list[dict[str, object]] = []

        for runbook in self._runbooks:
            matched_terms = query_terms.intersection(runbook.terms)

            if not matched_terms:
                continue

            # Simple overlap score: the proportion of query terms found.
            score = len(matched_terms) / len(query_terms)

            results.append(
                {
                    "title": runbook.title,
                    "source": runbook.source,
                    "score": round(score, 4),
                    "matched_terms": sorted(matched_terms),
                    "content": runbook.content,
                }
            )

        results.sort(
            key=lambda item: (
                -float(item["score"]),
                str(item["source"]),
            )
        )

        return results[:top_k]


def retrieve_runbooks(query: str, top_k: int = 3) -> list[dict[str, object]]:
    """Convenience function for retrieving relevant troubleshooting docs."""
    retriever = RunbookRetriever()
    return retriever.search(query, top_k=top_k)
