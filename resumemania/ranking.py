"""Eligibility and ranking rules. Plain Python, fully deterministic and tested.

Status of each submission:
    invalid     unreadable, too short or not a resume   -> not ranked, private reason
    irrelevant  shows none of the job's requirements     -> not ranked, private reason
    below       readable and relevant, under benchmark   -> private score only, never named
    eligible    at or above the benchmark                -> ranked

Rank order: score (high first), then required-skills component (high first), then the
earliest submission time. Ties that survive all three share... nothing: the earlier
submission wins, so every rank is unique and stable.

Public leaderboard: the top 10% of eligible students, rounded UP, at least 1 when anyone
is eligible. Nobody else appears, not even as a blank row.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

PUBLIC_SHARE = 0.10
DEFAULT_BENCHMARK = 60


class Status(str, Enum):
    INVALID = "invalid"
    IRRELEVANT = "irrelevant"
    BELOW = "below"
    ELIGIBLE = "eligible"


@dataclass(frozen=True)
class Entry:
    submission_id: int
    score: int
    required_component: float
    submitted_at: str  # ISO 8601, sorts lexically


@dataclass(frozen=True)
class Ranking:
    ordered_ids: tuple[int, ...]  # every eligible submission, best first
    visible_ids: tuple[int, ...]  # the public top slice

    def rank_of(self, submission_id: int) -> int | None:
        try:
            return self.ordered_ids.index(submission_id) + 1
        except ValueError:
            return None


def eligibility(score: int, benchmark: int, any_requirement_shown: bool) -> Status:
    if not any_requirement_shown:
        return Status.IRRELEVANT
    return Status.ELIGIBLE if score >= benchmark else Status.BELOW


def public_count(eligible: int, share: float = PUBLIC_SHARE) -> int:
    """Top 10% rounded up, minimum 1 when anyone is eligible."""
    if eligible <= 0:
        return 0
    return max(1, math.ceil(eligible * share - 1e-9))


def rank(entries: list[Entry]) -> Ranking:
    ordered = sorted(entries, key=lambda e: (-e.score, -e.required_component, e.submitted_at, e.submission_id))
    ids = tuple(e.submission_id for e in ordered)
    return Ranking(ordered_ids=ids, visible_ids=ids[: public_count(len(ids))])
