"""A rule-based stand-in for Gemini, for demo data only. Makes no network calls.

It answers the same structured questions the real agents ask, using keyword matching on the
resume's own lines. Results are rougher than Gemini's but go through the real validation gate,
scoring, ranking and leaderboard code. Never use it to judge real students.
"""

from __future__ import annotations

import json
import re

from resumemania.schemas import (
    Action,
    EvidenceMatch,
    FeedbackPlan,
    MatchResult,
    MatchStatus,
    ParsedResume,
    QualityFinding,
    QualityReview,
    Severity,
)
from resumemania.scoring import contains_term

SECTIONS = ("summary", "experience", "projects", "skills", "education", "certifications")
APPLIED = ("experience", "projects")
BULLET = re.compile(r"^\s*[•\-*▪●◦]\s*")
NUMBER = re.compile(r"\d")
MAX_FINDINGS = 4
STOP_WORDS = {"experience", "with", "and", "or", "the", "a", "in", "of", "for", "strong", "basic", "using",
              "such", "as", "similar", "knowledge", "hands-on", "building", "degree", "related", "field"}


class OfflineLLM:
    """Implements the StructuredLLM protocol without calling any model."""

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, *, model: str, system: str, prompt: str, schema: type, step: str):
        self.calls += 1
        resume = _fenced(prompt, "resume")
        lines = _sectioned_lines(resume)
        if schema is ParsedResume:
            return _parse(resume, lines)
        if schema is MatchResult:
            return _match(prompt, lines)
        if schema is QualityReview:
            return _quality(lines)
        if schema is FeedbackPlan:
            return _plan(prompt)
        raise NotImplementedError(f"OfflineLLM can't answer {schema.__name__}; campaigns must already exist.")


def _fenced(prompt: str, tag: str) -> str:
    match = re.search(rf"<{tag}>\n(.*)\n</{tag}>", prompt, re.DOTALL)
    return match.group(1) if match else ""


def _sectioned_lines(text: str) -> list[tuple[str, str]]:
    """(section, line) for every non-empty line, tracking the latest heading."""
    section = "header"
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = line.lower().rstrip(":")
        found = next((s for s in SECTIONS if heading.startswith(s)), None)
        if found and len(line.split()) <= 4:
            section = found
            continue
        out.append((section, line))
    return out


def _parse(resume: str, lines: list[tuple[str, str]]) -> ParsedResume:
    name = next((line for line in resume.splitlines() if line.strip()), "").strip()
    skills = [s.strip() for sec, line in lines if sec == "skills" for s in line.split(":")[-1].split(",")]
    present = {sec for sec, _ in lines}
    missing = [s.title() for s in SECTIONS if s not in present]
    return ParsedResume(name=name, skills=[s for s in skills if s][:30], missing_sections=missing)


def _terms(requirement: dict) -> list[str]:
    terms = [k for k in requirement.get("keywords", []) if k.strip()]
    if terms:
        return terms
    words = re.findall(r"[A-Za-z][A-Za-z+#./-]{2,}", requirement.get("text", ""))
    return [w for w in words if w.lower() not in STOP_WORDS][:4]


def _match(prompt: str, lines: list[tuple[str, str]]) -> MatchResult:
    block = re.search(r"Requirements:\n(.*?)\n\n<resume>", prompt, re.DOTALL)
    requirements = json.loads(block.group(1)) if block else []
    matches = []
    for req in requirements:
        terms = _terms(req)
        hits = [(sec, line) for sec, line in lines if any(contains_term(line, t) for t in terms)]
        applied = [h for h in hits if h[0] in APPLIED]
        education = req.get("category") == "education" and [h for h in hits if h[0] in ("education", "certifications")]
        if applied or education:
            sec, line = (applied or education)[0]
            status, note = MatchStatus.MATCHED, "Shown in the resume."
        elif hits:
            sec, line = hits[0]
            status, note = MatchStatus.PARTIAL, "Mentioned, but not shown in a project or job."
        else:
            matches.append(EvidenceMatch(requirement_id=req["id"], status=MatchStatus.MISSING,
                                         note="Not in the resume yet. You may have it but haven't shown it."))
            continue
        matches.append(EvidenceMatch(requirement_id=req["id"], status=status, evidence=[BULLET.sub("", line)],
                                     where=sec.title(), note=note))
    return MatchResult(matches=matches)


def _quality(lines: list[tuple[str, str]]) -> QualityReview:
    bullets = [(sec, BULLET.sub("", line)) for sec, line in lines if BULLET.match(line)]
    no_numbers = [(sec, b) for sec, b in bullets if not NUMBER.search(b)]
    findings = [
        QualityFinding(issue="No result or number", severity=Severity.MEDIUM, location=sec.title(), quote=b,
                       why_it_matters="A number shows the size of what you did.")
        for sec, b in no_numbers[:MAX_FINDINGS]
    ]
    with_numbers = len(bullets) - len(no_numbers)
    strengths = [f"{with_numbers} bullets show a measurable result."] if with_numbers else []
    if any(sec == "projects" for sec, _ in lines):
        strengths.append("Projects section with real work.")
    return QualityReview(findings=findings, strengths=strengths)


def _plan(prompt: str) -> FeedbackPlan:
    block = re.search(r"Findings so far:\n(.*?)\n\n<resume>", prompt, re.DOTALL)
    context = json.loads(block.group(1)) if block else {}
    actions = [
        Action(title=f"Show evidence for {gap['id']}",
               detail="Add a project or job bullet that proves this requirement, if it's true for you.",
               priority=Severity.HIGH if gap["status"] == "missing" else Severity.MEDIUM, requirement_ids=[gap["id"]])
        for gap in context.get("gaps", [])[:4]
    ]
    if context.get("writing_findings"):
        actions.append(Action(title="Add results to your bullets",
                              detail="Say what changed and by how much, using real numbers.", priority=Severity.LOW))
    return FeedbackPlan(actions=actions)
