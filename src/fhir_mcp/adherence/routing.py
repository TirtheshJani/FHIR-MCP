from __future__ import annotations

import re
from enum import StrEnum
from typing import Protocol


class Intent(StrEnum):
    STRUCTURED = "structured"
    NARRATIVE = "narrative"
    AMBIGUOUS = "ambiguous"


class Router(Protocol):
    def detect(self, question: str) -> Intent: ...


_STRUCTURED_PATTERNS = [
    re.compile(r"\bdid\b.*\btake\b", re.IGNORECASE),
    re.compile(r"\brefill", re.IGNORECASE),
    re.compile(r"\bhow many\b", re.IGNORECASE),
    re.compile(
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?<![a-z])\d{4}(?![0-9a-z])", re.IGNORECASE),
]

_NARRATIVE_PATTERNS = [
    re.compile(r"\bdescribe\b", re.IGNORECASE),
    re.compile(r"\bsummari[sz]e\b", re.IGNORECASE),
    re.compile(r"\boverall\b", re.IGNORECASE),
    re.compile(r"\bpattern\b", re.IGNORECASE),
]


class HeuristicRouter:
    def detect(self, question: str) -> Intent:
        structured_hits = sum(1 for p in _STRUCTURED_PATTERNS if p.search(question))
        narrative_hits = sum(1 for p in _NARRATIVE_PATTERNS if p.search(question))
        if structured_hits > 0 and narrative_hits == 0:
            return Intent.STRUCTURED
        if narrative_hits > 0 and structured_hits == 0:
            return Intent.NARRATIVE
        return Intent.AMBIGUOUS
