"""Remove contact details and IDs before a resume is shown to other students."""

from __future__ import annotations

import re

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"(?i)\b(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com|gitlab\.com|"
                r"twitter\.com|x\.com|instagram\.com|facebook\.com)/\S*"), "[link]"),
    (re.compile(r"(?i)\bhttps?://\S+"), "[link]"),
    (re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)"), "[phone]"),
    # Aadhaar-style 12 digits, PAN, passport-like IDs and roll numbers.
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[id]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[id]"),
    (re.compile(r"(?i)\b(?:roll|enrol(?:l)?ment|student)\s*(?:no\.?|number|id)\s*[:#-]?\s*\S+"), "[id]"),
    (re.compile(r"(?i)\b(?:address|addr\.?)\s*[:-].*"), "[address]"),
    (re.compile(r"(?i)\b\d{1,5}[,\s]+[\w\s]{2,40}\b(?:road|rd|street|st|lane|nagar|colony|sector|apartment|flat)\b[^\n]*"),
     "[address]"),
    (re.compile(r"\b\d{6}\b"), "[pin]"),  # Indian PIN code
)


def redact_pii(text: str, full_name: str = "") -> str:
    """Return a copy with emails, phones, links, IDs, addresses and the student's name masked."""
    redacted = text
    for pattern, replacement in _RULES:
        redacted = pattern.sub(replacement, redacted)
    for part in {p for p in full_name.split() if len(p) > 1}:
        redacted = re.sub(rf"\b{re.escape(part)}\b", "[name]", redacted, flags=re.IGNORECASE)
    return redacted
