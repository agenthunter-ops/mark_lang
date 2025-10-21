"""Utilities for ingesting business briefs into structured representations."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class BusinessBrief:
    """Lightweight container for a business brief."""

    title: str
    content: str
    source: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        """Return a canonical text representation of the brief."""

        header = f"Title: {self.title}\n"
        body = self.content.strip()
        if self.tags:
            tags_line = ", ".join(sorted(self.tags))
            header += f"Tags: {tags_line}\n"
        if self.source:
            header += f"Source: {self.source}\n"
        return f"{header}\n{body}".strip()


class BriefIngestor:
    """Load briefs from strings, files, or batch iterables."""

    def __init__(self, default_title: str = "Untitled Brief") -> None:
        self.default_title = default_title

    def from_text(
        self, text: str, *, title: Optional[str] = None, tags: Optional[Iterable[str]] = None
    ) -> BusinessBrief:
        """Create a :class:`BusinessBrief` from raw text."""

        normalized_title = title or self._derive_title(text)
        normalized_tags = list(tags) if tags else []
        return BusinessBrief(
            title=normalized_title,
            content=text.strip(),
            tags=normalized_tags,
            source="inline",
        )

    def from_path(
        self, path: str | Path, *, title: Optional[str] = None, tags: Optional[Iterable[str]] = None
    ) -> BusinessBrief:
        """Load a brief from a text document."""

        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        inferred_title = title or self._derive_title(
            content, fallback=file_path.stem, prefer_fallback=True
        )
        return BusinessBrief(
            title=inferred_title,
            content=content.strip(),
            source=str(file_path.resolve()),
            tags=list(tags) if tags else [],
        )

    def batch_from_paths(
        self, paths: Iterable[str | Path], *, tags: Optional[Iterable[str]] = None
    ) -> list[BusinessBrief]:
        """Convenience helper to load multiple briefs at once."""

        return [self.from_path(path, tags=tags) for path in paths]

    def _derive_title(
        self, text: str, *, fallback: Optional[str] = None, prefer_fallback: bool = False
    ) -> str:
        """Infer a brief title using the first line of text or a fallback."""

        first_line = next((line.strip() for line in text.splitlines() if line.strip()), None)
        if first_line and not prefer_fallback:
            return first_line[:80]
        return fallback or self.default_title
