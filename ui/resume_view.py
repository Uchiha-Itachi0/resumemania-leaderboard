"""Render a redacted resume as a readable document instead of a wall of plain text.

PDF text arrives as short wrapped lines. This rebuilds paragraphs and bullets, turns known
section names into headings, and swaps the redacted header (name, contact line) for the
student's GitHub handle and a "contact details removed" note.
"""

from __future__ import annotations

import re

from .components import esc

SECTION_WORDS = ("summary", "profile", "objective", "experience", "work experience", "projects", "skills",
                 "technical skills", "education", "certifications", "certifications and achievements",
                 "achievements", "awards", "publications")
BULLET = re.compile(r"^\s*[•\-*▪●◦]\s*")
REDACTED_ONLY = re.compile(r"^(\s*\[(name|email|phone|link|id|address|pin)\]\s*[·|,]?\s*)+$")
SENTENCE_END = (".", "!", "?", ":")
DATE_LINE = re.compile(r"^((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+)?(19|20)\d\d\b.*", re.IGNORECASE)
LINK_ONLY = re.compile(r"^(\[link\]\s*[·|,]?\s*)+$")


def _is_heading(line: str) -> bool:
    clean = line.strip().rstrip(":").lower()
    return clean in SECTION_WORDS or (line.isupper() and len(line.split()) <= 4)


def _blocks(text: str) -> list[tuple[str, str]]:
    """(kind, text) where kind is heading, bullet or line; wrapped lines are joined back."""
    blocks: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if _is_heading(line):
            blocks.append(("heading", line.rstrip(":")))
        elif BULLET.match(line):
            blocks.append(("bullet", BULLET.sub("", line)))
        elif blocks and blocks[-1][0] in ("bullet", "line") and not blocks[-1][1].endswith(SENTENCE_END) \
                and line[:1].islower():
            kind, previous = blocks[-1]
            blocks[-1] = (kind, f"{previous} {line}")
        else:
            blocks.append(("line", line))
    return blocks


def resume_html(redacted_text: str, github_username: str) -> str:
    blocks = _blocks(redacted_text)
    # Drop header lines that are only redaction markers (the name and contact line).
    header_removed = False
    kept = []
    for i, (kind, text) in enumerate(blocks):
        if i < 4 and kind == "line" and (REDACTED_ONLY.match(text) or text.count("[") >= 2):
            header_removed = True
            continue
        kept.append((kind, text))

    parts = [f"<div class='rm-cv-name'>@{esc(github_username)}</div>"]
    if header_removed:
        parts.append("<span class='rm-pill mono'>Contact details removed</span>")
    open_list = False
    for kind, text in kept:
        if kind == "bullet":
            if not open_list:
                parts.append("<ul>")
                open_list = True
            parts.append(f"<li>{esc(text)}</li>")
            continue
        if open_list:
            parts.append("</ul>")
            open_list = False
        if kind == "heading":
            parts.append(f"<div class='rm-cv-h'>{esc(text)}</div>")
        elif LINK_ONLY.match(text):
            continue
        elif DATE_LINE.match(text):
            parts.append(f"<p class='rm-cv-meta'>{esc(text)}</p>")
        elif " · " in text and ":" not in text and len(text) < 120:
            parts.append(f"<p class='rm-cv-title'>{esc(text.replace(' · [link]', ''))}</p>")
        else:
            parts.append(f"<p>{_label_value(text)}</p>")
    if open_list:
        parts.append("</ul>")
    return f"<article class='rm-cv'>{''.join(parts)}</article>"


def _label_value(text: str) -> str:
    """Bold the label in 'Skills: a, b, c' style lines."""
    label, sep, rest = text.partition(":")
    if sep and 0 < len(label) <= 32 and rest.strip():
        return f"<strong>{esc(label)}:</strong>{esc(rest)}"
    return esc(text)
