"""Extraction utilities for creative briefs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .brief_ingest import BusinessBrief


@dataclass
class CreativeBrief:
    """Structured creative brief ready for campaign planning."""

    goals: str
    audience: str
    messaging: str
    timeframe: str
    source_title: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "goals": self.goals,
            "audience": self.audience,
            "messaging": self.messaging,
            "timeframe": self.timeframe,
            "source_title": self.source_title,
        }


DEFAULT_VALUES = {
    "goals": "Increase brand awareness and generate qualified leads.",
    "audience": "Primary decision makers within the target industry vertical.",
    "messaging": "Highlight value proposition, proof points, and call-to-action.",
    "timeframe": "Launch within the next fiscal quarter with bi-weekly reporting.",
}


class CreativeBriefExtractor:
    """Extract structured data from a :class:`BusinessBrief`."""

    def __init__(self, defaults: Optional[Dict[str, str]] = None) -> None:
        self.defaults = defaults or DEFAULT_VALUES

    def extract(self, brief: BusinessBrief) -> CreativeBrief:
        sections = self._segment_sections(brief.content)
        return CreativeBrief(
            goals=self._resolve_value("goals", sections),
            audience=self._resolve_value("audience", sections),
            messaging=self._resolve_value("messaging", sections),
            timeframe=self._resolve_value("timeframe", sections),
            source_title=brief.title,
        )

    def detect_gaps(self, creative_brief: CreativeBrief) -> Dict[str, str]:
        """Return prompts for any fields that still rely on defaults."""

        prompts: Dict[str, str] = {}
        for field, default in self.defaults.items():
            value = getattr(creative_brief, field)
            if value == default:
                prompts[field] = (
                    f"Please provide specific {field} details for '{creative_brief.source_title}'"
                )
        return prompts

    def _segment_sections(self, content: str) -> Dict[str, str]:
        normalized = content.lower()
        sections: Dict[str, str] = {}
        for field in DEFAULT_VALUES:
            marker = f"{field}:"
            start = normalized.find(marker)
            if start == -1:
                continue
            start_index = start + len(marker)
            end_index = self._find_section_end(normalized, start_index)
            sections[field] = content[start_index:end_index].strip().rstrip("\n")
        return sections

    def _resolve_value(self, field: str, sections: Dict[str, str]) -> str:
        return sections.get(field, self.defaults[field])

    def _find_section_end(self, normalized: str, start_index: int) -> int:
        next_indices = [normalized.find(f"{field}:", start_index) for field in DEFAULT_VALUES]
        candidates = [idx for idx in next_indices if idx != -1]
        return min(candidates) if candidates else len(normalized)
