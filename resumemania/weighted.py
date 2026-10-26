"""Weighted, explainable campaign score. Plain Python, no AI.

Five components, each 0 to 1, from the matcher's per-requirement verdicts:

    required skills   must-have skill requirements shown          default 40%
    evidence          shown requirements proved in Experience or   default 25%
                      Projects (applied), not just listed in Skills
    experience        experience requirements shown                default 15%
    preferred skills  nice-to-have skill requirements shown        default 10%
    education         degree and certification requirements shown  default 10%

Credit per requirement: shown 1, partly shown 0.5, not shown 0.
A component with no requirements in the job is dropped and its weight shared
proportionally across the others, so a job with no education ask is not penalised.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .schemas import Category, EvidenceMatch, JobRequirements, MatchStatus, Priority, Requirement

WEIGHTED_SCORING_VERSION = "weighted-v1"
STATUS_CREDIT = {MatchStatus.MATCHED: 1.0, MatchStatus.PARTIAL: 0.5, MatchStatus.MISSING: 0.0}
APPLIED_SECTIONS = ("experience", "project", "internship", "work")

COMPONENT_LABELS = {
    "required": "Required skills",
    "evidence": "Evidence in projects and work",
    "experience": "Experience",
    "preferred": "Preferred skills",
    "education": "Education and certifications",
}
DEFAULT_WEIGHTS = {"required": 40, "evidence": 25, "experience": 15, "preferred": 10, "education": 10}


@dataclass(frozen=True)
class ScoringConfig:
    weights: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    def __post_init__(self) -> None:
        unknown = set(self.weights) - set(COMPONENT_LABELS)
        if unknown:
            raise ValueError(f"Unknown score components: {', '.join(sorted(unknown))}")
        if any(w < 0 for w in self.weights.values()):
            raise ValueError("Weights can't be negative.")
        if sum(self.weights.values()) <= 0:
            raise ValueError("At least one weight must be above 0.")


@dataclass(frozen=True)
class Component:
    key: str
    label: str
    value: float | None  # None when the job has no requirements for it
    weight: float  # effective weight after redistribution, 0 to 1


@dataclass(frozen=True)
class ScoreBreakdown:
    total: int
    components: tuple[Component, ...]
    version: str = WEIGHTED_SCORING_VERSION

    def component(self, key: str) -> Component:
        return next(c for c in self.components if c.key == key)


def compute_breakdown(
    job: JobRequirements, matches: list[EvidenceMatch], config: ScoringConfig | None = None
) -> ScoreBreakdown:
    config = config or ScoringConfig()
    by_id = {m.requirement_id: m for m in matches}

    def credit(reqs: list[Requirement]) -> float | None:
        if not reqs:
            return None
        return sum(STATUS_CREDIT[_status(by_id, r.id)] for r in reqs) / len(reqs)

    skills = [r for r in job.requirements if r.category == Category.SKILL]
    raw = {
        "required": credit([r for r in skills if r.priority == Priority.MUST]),
        "evidence": _applied_share(job, by_id),
        "experience": credit([r for r in job.requirements if r.category == Category.EXPERIENCE]),
        "preferred": credit([r for r in skills if r.priority == Priority.NICE]),
        "education": credit([r for r in job.requirements if r.category == Category.EDUCATION]),
    }
    active = {k: config.weights.get(k, 0) for k, v in raw.items() if v is not None}
    active_total = sum(active.values())
    components = tuple(
        Component(
            key=key,
            label=COMPONENT_LABELS[key],
            value=value,
            weight=(active.get(key, 0) / active_total) if active_total and value is not None else 0.0,
        )
        for key, value in raw.items()
    )
    total = sum((c.value or 0.0) * c.weight for c in components)
    return ScoreBreakdown(total=_round_half_up(100 * total), components=components)


def _status(by_id: dict[str, EvidenceMatch], requirement_id: str) -> MatchStatus:
    match = by_id.get(requirement_id)
    return match.status if match else MatchStatus.MISSING


def _applied_share(job: JobRequirements, by_id: dict[str, EvidenceMatch]) -> float | None:
    """Of the requirements the resume shows at all, the share proved in work or projects."""
    if not job.requirements:
        return None
    shown = [by_id[r.id] for r in job.requirements
             if r.id in by_id and by_id[r.id].status != MatchStatus.MISSING]
    if not shown:
        return 0.0
    applied = sum(1 for m in shown if any(s in m.where.lower() for s in APPLIED_SECTIONS))
    return applied / len(shown)


def _round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))
