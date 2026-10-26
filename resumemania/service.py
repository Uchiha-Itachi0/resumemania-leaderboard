"""Everything the UI may do. No accounts: a student is the GitHub username linked in their resume.

Privacy rules enforced here, not in the UI:
- The leaderboard returns only the top 10% of eligible students, nothing about anyone else.
- Shared resumes are redacted at read time and only when the student opted in.
- Staff can open eligible candidates only. Below-benchmark reports are never returned to staff.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from . import agents, github
from .agents import Models
from .ingest import ExtractedText, IngestError, validate_jd
from .llm import LLMError, StructuredLLM
from .pipeline import run_analysis
from .ranking import DEFAULT_BENCHMARK, PUBLIC_SHARE, PUBLIC_SHARE_OPTIONS, Entry, Status, eligibility, rank
from .redact import redact_pii
from .schemas import Analysis, MatchStatus
from .storage import Campaign, Evaluation, Snapshot, Storage, Submission, now
from .weighted import WEIGHTED_SCORING_VERSION, ScoringConfig, compute_breakdown

logger = logging.getLogger(__name__)

FAILED = "failed"  # the AI could not finish; not a judgement on the resume
RANKING_VERSION = "rank-v1"
MIN_TITLE = 3


class NotAllowed(PermissionError):
    """This would expose data the rules keep private. The message is safe to show."""


@dataclass(frozen=True)
class StudentResult:
    campaign: Campaign
    submission: Submission
    evaluation: Evaluation
    rank: int | None
    eligible_count: int
    on_public_board: bool


@dataclass(frozen=True)
class LeaderboardRow:
    rank: int
    github_username: str
    score: int
    shared_resume: str | None


@dataclass(frozen=True)
class RankedCandidate:
    rank: int
    submission_id: int
    github_username: str
    score: int
    required_component: float
    on_public_board: bool


@dataclass(frozen=True)
class Dashboard:
    campaign: Campaign
    submitted: int
    status_counts: dict[str, int]
    distribution: dict[str, int]  # score band -> count, relevant resumes only
    candidates: list[RankedCandidate]  # eligible only, ranked
    problems: list[tuple[str, str]]  # (github username, reason) for unreadable or failed resumes


class CampaignService:
    def __init__(self, store: Storage, llm: Callable[[], StructuredLLM], models: Models):
        self._store = store
        self._llm = llm
        self._models = models

    # ---------- campaigns ----------

    def create_campaign(self, title: str, jd_text: str, cohort: str = "", benchmark: int = DEFAULT_BENCHMARK,
                        weights: dict[str, int] | None = None, public_share: float = PUBLIC_SHARE) -> Campaign:
        if len(title.strip()) < MIN_TITLE:
            raise IngestError("Give the campaign a title, like 'Data Analyst Intern 2026'.")
        if not 0 <= benchmark <= 100:
            raise IngestError("The benchmark must be between 0 and 100.")
        if public_share not in PUBLIC_SHARE_OPTIONS:
            raise IngestError("Pick how many students the public leaderboard shows.")
        config = ScoringConfig(weights=weights or ScoringConfig().weights)
        validate_jd(jd_text)
        job = agents.analyze_jd(self._llm(), self._models, jd_text, title)
        if not job.requirements:
            raise IngestError("We couldn't find any requirements in that job description.")
        return self._store.create_campaign(title.strip(), jd_text, job, cohort.strip(), benchmark, config.weights,
                                           public_share)

    def set_public_share(self, campaign_id: int, public_share: float) -> Snapshot:
        """Change how many students the public board shows, then re-rank."""
        self.campaign(campaign_id)
        if public_share not in PUBLIC_SHARE_OPTIONS:
            raise IngestError("Pick how many students the public leaderboard shows.")
        self._store.set_public_share(campaign_id, public_share)
        return self.recalculate(campaign_id)

    def campaigns(self) -> list[Campaign]:
        return self._store.list_campaigns()

    def campaign(self, campaign_id: int) -> Campaign:
        campaign = self._store.get_campaign(campaign_id)
        if campaign is None:
            raise IngestError("That campaign doesn't exist any more.")
        return campaign

    # ---------- students ----------

    def submit(self, campaign_id: int, resume: ExtractedText, consent: bool) -> StudentResult:
        """Score a resume. The GitHub link in it is the student's ID, and a second upload
        with the same GitHub username replaces the first."""
        campaign = self.campaign(campaign_id)
        username = github.require_from_resume(resume.text)
        submission = self._store.replace_submission(campaign_id, username, github.key(username), resume.text,
                                                    resume.source, resume.page_count, consent)
        evaluation = self._evaluate(campaign, submission, resume)
        self._store.save_evaluation(evaluation)
        snapshot = self.recalculate(campaign_id)
        position = snapshot.eligible_ids.index(submission.id) + 1 if submission.id in snapshot.eligible_ids else None
        return StudentResult(campaign, submission, evaluation, position, len(snapshot.eligible_ids),
                             submission.id in snapshot.visible_ids)

    # ---------- shared ----------

    def leaderboard(self, campaign_id: int) -> tuple[list[LeaderboardRow], int]:
        """(top 10% rows, number of eligible students). Shared resumes are redacted here."""
        self.campaign(campaign_id)
        snapshot = self._store.latest_snapshot(campaign_id)
        if snapshot is None:
            return [], 0
        rows = []
        for position, sid in enumerate(snapshot.visible_ids, 1):
            sub = self._store.get_submission(sid)
            ev = self._store.get_evaluation(sid)
            if sub is None or ev is None:
                continue
            shared = None
            if sub.consent_to_share:
                real_name = ev.analysis.resume.name if ev.analysis else ""
                shared = redact_pii(sub.content, real_name)
            rows.append(LeaderboardRow(position, sub.github_username, ev.score, shared))
        return rows, len(snapshot.eligible_ids)

    def dashboard(self, campaign_id: int) -> Dashboard:
        campaign = self.campaign(campaign_id)
        subs = self._store.submissions(campaign_id)
        evals = {s.id: self._store.get_evaluation(s.id) for s in subs}
        names = {s.id: s.github_username for s in subs}
        counts = {s.value: 0 for s in Status} | {FAILED: 0}
        bands = {b: 0 for b in ("0-19", "20-39", "40-59", "60-79", "80-100")}
        problems: list[tuple[str, str]] = []
        for sub in subs:
            ev = evals[sub.id]
            if ev is None:
                continue
            counts[ev.status] = counts.get(ev.status, 0) + 1
            if ev.status in (Status.BELOW.value, Status.ELIGIBLE.value):
                bands[_band(ev.score)] += 1
            if ev.status in (Status.INVALID.value, FAILED):
                problems.append((names[sub.id], ev.message))
        snapshot = self._store.latest_snapshot(campaign_id)
        candidates = []
        if snapshot:
            for position, sid in enumerate(snapshot.eligible_ids, 1):
                ev = evals.get(sid)
                if ev is None:
                    continue
                candidates.append(RankedCandidate(position, sid, names[sid], ev.score, ev.required_component,
                                                  sid in snapshot.visible_ids))
        return Dashboard(campaign, len(subs), counts, bands, candidates, problems)

    def candidate_detail(self, campaign_id: int, submission_id: int) -> Evaluation:
        """Staff may open eligible candidates only. Below-benchmark reports stay with the student."""
        submission = self._store.get_submission(submission_id)
        if submission is None or submission.campaign_id != campaign_id:
            raise NotAllowed("That submission isn't part of this campaign.")
        evaluation = self._store.get_evaluation(submission_id)
        if evaluation is None or evaluation.status != Status.ELIGIBLE.value:
            raise NotAllowed("Only eligible students' reports can be opened by staff.")
        return evaluation

    def recalculate(self, campaign_id: int) -> Snapshot:
        campaign = self.campaign(campaign_id)
        entries = []
        for sub in self._store.submissions(campaign_id):
            ev = self._store.get_evaluation(sub.id)
            if ev and ev.status == Status.ELIGIBLE.value:
                entries.append(Entry(sub.id, ev.score, ev.required_component, sub.created_at))
        ranking = rank(entries, campaign.public_share)
        snapshot = Snapshot(campaign_id, now(), ranking.ordered_ids, ranking.visible_ids, RANKING_VERSION)
        self._store.save_snapshot(snapshot)
        return snapshot

    # ---------- internals ----------

    def _evaluate(self, campaign: Campaign, submission: Submission, resume: ExtractedText) -> Evaluation:
        def result(status: str, message: str, analysis: Analysis | None = None, score: int = 0,
                   required: float = 0.0, breakdown: list[dict] | None = None) -> Evaluation:
            return Evaluation(submission.id, status, score, required,
                              analysis.keyword_coverage if analysis else 0.0, breakdown or [], analysis,
                              message, WEIGHTED_SCORING_VERSION, now())

        try:
            analysis = run_analysis(self._llm(), self._models, resume, campaign.job_description,
                                    campaign.title, job=campaign.job)
        except IngestError as exc:
            return result(Status.INVALID.value, str(exc))
        except LLMError as exc:
            logger.warning("evaluation failed submission=%d", submission.id)
            return result(FAILED, str(exc))

        breakdown = compute_breakdown(analysis.job, analysis.matches, ScoringConfig(weights=campaign.weights))
        shown = any(m.status != MatchStatus.MISSING for m in analysis.matches)
        status = eligibility(breakdown.total, campaign.benchmark, shown)
        message = {
            Status.IRRELEVANT: "This resume doesn't show any of the job's requirements, so it isn't ranked.",
            Status.BELOW: f"Below the {campaign.benchmark}% benchmark. Your score isn't shown to anyone else.",
            Status.ELIGIBLE: f"At or above the {campaign.benchmark}% benchmark. You're ranked.",
        }[status]
        rows = [{"key": c.key, "label": c.label, "value": c.value, "weight": c.weight} for c in breakdown.components]
        analysis = analysis.model_copy(update={"score": breakdown.total, "scoring_version": breakdown.version})
        return result(status.value, message, analysis, breakdown.total, breakdown.component("required").value or 0.0,
                      rows)


def _band(score: int) -> str:
    if score >= 80:
        return "80-100"
    low = (score // 20) * 20
    return f"{low}-{low + 19}"
