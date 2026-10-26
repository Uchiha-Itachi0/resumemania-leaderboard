"""Leaderboard rules: weighted score, eligibility, ranking, privacy, permissions, redaction."""

from __future__ import annotations

import pytest

from resumemania import github
from resumemania.agents import Models
from resumemania.ingest import from_paste
from resumemania.llm import FakeLLM, LLMError
from resumemania.ranking import Entry, Status, eligibility, public_count, rank
from resumemania.redact import redact_pii
from resumemania.schemas import (
    Category,
    EvidenceMatch,
    JobRequirements,
    MatchResult,
    MatchStatus,
    ParsedResume,
    Priority,
    Requirement,
)
from resumemania.service import CampaignService, NotAllowed
from resumemania.weighted import ScoringConfig, compute_breakdown

# ---------- weighted score ----------


def _job(*reqs: tuple[str, Priority, Category]) -> JobRequirements:
    return JobRequirements(requirements=[Requirement(id=i, text=i, priority=p, category=c) for i, p, c in reqs])


def _m(rid: str, status: MatchStatus, where: str = "Experience") -> EvidenceMatch:
    return EvidenceMatch(requirement_id=rid, status=status, where=where,
                         evidence=["x"] if status != MatchStatus.MISSING else [])


def test_weighted_score_all_components():
    job = _job(("R1", Priority.MUST, Category.SKILL), ("R2", Priority.NICE, Category.SKILL),
               ("R3", Priority.MUST, Category.EXPERIENCE), ("R4", Priority.NICE, Category.EDUCATION))
    matches = [_m("R1", MatchStatus.MATCHED), _m("R2", MatchStatus.PARTIAL, "Skills"),
               _m("R3", MatchStatus.MATCHED, "Projects"), _m("R4", MatchStatus.MISSING)]
    b = compute_breakdown(job, matches)
    # required 1.0*.4 + evidence (2 of 3 applied) .667*.25 + experience 1*.15 + preferred .5*.1 + edu 0
    assert b.total == round(100 * (0.4 + 0.25 * 2 / 3 + 0.15 + 0.05))
    assert b.component("evidence").value == pytest.approx(2 / 3)


def test_weighted_score_redistributes_missing_components():
    job = _job(("R1", Priority.MUST, Category.SKILL))  # no nice, experience or education asks
    b = compute_breakdown(job, [_m("R1", MatchStatus.MATCHED, "Skills")])
    # Only required (40) and evidence (25) are active: 1.0*40/65 + 0.0*25/65
    assert b.total == round(100 * 40 / 65)
    assert b.component("education").value is None
    assert b.component("education").weight == 0


def test_weighted_score_respects_custom_weights():
    job = _job(("R1", Priority.MUST, Category.SKILL), ("R2", Priority.NICE, Category.SKILL))
    matches = [_m("R1", MatchStatus.MISSING), _m("R2", MatchStatus.MATCHED)]
    b = compute_breakdown(job, matches, ScoringConfig(weights={"preferred": 100, "required": 0}))
    assert b.total == 100


def test_scoring_config_rejects_bad_weights():
    with pytest.raises(ValueError):
        ScoringConfig(weights={"luck": 10})
    with pytest.raises(ValueError):
        ScoringConfig(weights={"required": 0})


# ---------- eligibility and ranking ----------


@pytest.mark.parametrize(("eligible", "shown"), [(0, 0), (1, 1), (5, 1), (10, 1), (11, 2), (20, 2), (21, 3), (95, 10)])
def test_public_count_rounds_up_with_minimum_one(eligible, shown):
    assert public_count(eligible) == shown


def test_eligibility_rules():
    assert eligibility(90, 60, any_requirement_shown=False) == Status.IRRELEVANT
    assert eligibility(59, 60, any_requirement_shown=True) == Status.BELOW
    assert eligibility(60, 60, any_requirement_shown=True) == Status.ELIGIBLE


def test_rank_tie_breaks_by_required_then_time():
    entries = [
        Entry(1, 80, 0.5, "2026-10-27T10:00:02"),
        Entry(2, 80, 0.9, "2026-10-27T10:00:03"),
        Entry(3, 80, 0.9, "2026-10-27T10:00:01"),
        Entry(4, 95, 0.1, "2026-10-27T10:00:09"),
    ]
    result = rank(entries)
    assert result.ordered_ids == (4, 3, 2, 1)
    assert result.visible_ids == (4,)
    assert result.rank_of(2) == 3
    assert result.rank_of(99) is None


# ---------- redaction ----------


def test_redact_pii_masks_contact_details_and_name():
    text = ("Priya Sharma\npriya@example.com | +91 98765 43210 | linkedin.com/in/priya | "
            "github.com/priya\nAddress: 12 MG Road, Pune 411001\nAadhaar 1234 5678 9012\nBuilt SQL dashboards")
    out = redact_pii(text, "Priya Sharma")
    for secret in ("priya@example.com", "98765", "linkedin.com/in/priya", "github.com/priya", "MG Road",
                   "411001", "1234 5678 9012", "Priya", "Sharma"):
        assert secret not in out
    assert "Built SQL dashboards" in out


# ---------- github usernames ----------


@pytest.mark.parametrize(("raw", "expected"), [
    ("octocat", "octocat"), ("@Octo-Cat", "Octo-Cat"), ("https://github.com/Uchiha-Itachi0", "Uchiha-Itachi0"),
    ("github.com/priya/", "priya"),
])
def test_github_normalise_accepts(raw, expected):
    assert github.normalise(raw) == expected


@pytest.mark.parametrize("raw", ["", "-bad", "bad-", "two--hyphens", "has space", "a" * 40, "settings"])
def test_github_normalise_rejects(raw):
    with pytest.raises(github.InvalidUsername):
        github.normalise(raw)


def test_github_from_resume():
    assert github.from_resume("Links: linkedin.com/in/x · github.com/Uchiha-Itachi0/PAYTM-BAHI") == "Uchiha-Itachi0"
    assert github.from_resume("no links here") is None


# ---------- service: a full campaign ----------


def _llm_for(job: JobRequirements, status_by_req: dict[str, MatchStatus], name: str = "Priya Sharma") -> FakeLLM:
    from resumemania.schemas import FeedbackPlan, QualityReview

    return FakeLLM({
        JobRequirements: job,
        ParsedResume: ParsedResume(name=name),
        MatchResult: MatchResult(matches=[_m(r, s) for r, s in status_by_req.items()]),
        QualityReview: QualityReview(),
        FeedbackPlan: FeedbackPlan(),
    })


class Switchable:
    """Lets each test swap which fake model answers the next call."""

    def __init__(self, llm: FakeLLM):
        self.current = llm

    def __call__(self) -> FakeLLM:
        return self.current


@pytest.fixture
def campaign_setup(storage, jd_text):
    job = _job(("R1", Priority.MUST, Category.SKILL), ("R2", Priority.MUST, Category.SKILL),
               ("R3", Priority.NICE, Category.SKILL))
    switch = Switchable(_llm_for(job, {}))
    svc = CampaignService(storage, switch, Models("f", "s"))
    campaign = svc.create_campaign("Data Analyst Intern", jd_text, "CSE 2026", benchmark=60)
    return svc, switch, job, campaign


def _submit(svc, switch, job, handle, campaign, statuses, resume_text, consent=False):
    switch.current = _llm_for(job, statuses)
    return svc.submit(campaign.id, handle, from_paste(resume_text), consent)


M, P, X = MatchStatus.MATCHED, MatchStatus.PARTIAL, MatchStatus.MISSING


def test_campaign_flow_ranks_and_hides_below_benchmark(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    top = _submit(svc, switch, job, "asha", campaign, {"R1": M, "R2": M, "R3": M}, resume_text, consent=True)
    mid = _submit(svc, switch, job, "ben", campaign, {"R1": M, "R2": P, "R3": X}, resume_text)
    low = _submit(svc, switch, job, "cara", campaign, {"R1": X, "R2": X, "R3": P}, resume_text)

    assert top.evaluation.status == "eligible" and top.rank == 1 and top.on_public_board
    assert mid.evaluation.status == "eligible" and mid.rank == 2 and not mid.on_public_board
    assert low.evaluation.status == "below" and low.rank is None

    board, eligible = svc.leaderboard(campaign.id)
    assert [r.github_username for r in board] == ["asha"]  # top 10% of 2 eligible = 1
    assert eligible == 2
    shared = board[0].shared_resume
    assert shared is not None
    for secret in ("priya.sharma@example.com", "98765", "Priya", "Sharma"):
        assert secret not in shared

    dash = svc.dashboard(campaign.id)
    assert dash.status_counts["eligible"] == 2 and dash.status_counts["below"] == 1
    assert [c.github_username for c in dash.candidates] == ["asha", "ben"]  # cara never listed
    assert sum(dash.distribution.values()) == 3


def test_reupload_replaces_the_old_entry(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    _submit(svc, switch, job, "asha", campaign, {"R1": M, "R2": M, "R3": P}, resume_text)
    _submit(svc, switch, job, "Ben", campaign, {"R1": M, "R2": P, "R3": X}, resume_text)
    improved = _submit(svc, switch, job, "github.com/ben", campaign, {"R1": M, "R2": M, "R3": M}, resume_text)
    assert improved.rank == 1
    assert svc.dashboard(campaign.id).submitted == 2  # Ben counted once, case-insensitive
    assert [c.github_username for c in svc.dashboard(campaign.id).candidates] == ["ben", "asha"]


def test_unshared_resume_is_not_shown(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    _submit(svc, switch, job, "asha", campaign, {"R1": M, "R2": M, "R3": M}, resume_text, consent=False)
    assert svc.leaderboard(campaign.id)[0][0].shared_resume is None


def test_irrelevant_invalid_and_failed_are_not_ranked(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    irrelevant = _submit(svc, switch, job, "asha", campaign, {"R1": X, "R2": X, "R3": X}, resume_text)
    invalid = _submit(svc, switch, job, "ben", campaign, {}, "too short")
    switch.current = FakeLLM({ParsedResume: LLMError("Gemini is busy")})
    failed = svc.submit(campaign.id, "cara", from_paste(resume_text), False)

    assert irrelevant.evaluation.status == "irrelevant"
    assert invalid.evaluation.status == "invalid" and "resume" in invalid.evaluation.message
    assert failed.evaluation.status == "failed"
    assert svc.leaderboard(campaign.id) == ([], 0)
    assert {name for name, _ in svc.dashboard(campaign.id).problems} == {"ben", "cara"}


def test_bad_github_username_is_rejected_before_scoring(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    with pytest.raises(github.InvalidUsername):
        _submit(svc, switch, job, "not a username", campaign, {"R1": M}, resume_text)
    assert switch.current.calls == []


def test_staff_cannot_open_below_benchmark_reports(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    low = _submit(svc, switch, job, "asha", campaign, {"R1": P, "R2": X, "R3": X}, resume_text)  # 47%
    with pytest.raises(NotAllowed, match="eligible"):
        svc.candidate_detail(campaign.id, low.submission.id)
    other = svc.create_campaign("Other job", resume_text * 2)
    top = _submit(svc, switch, job, "ben", campaign, {"R1": M, "R2": M, "R3": M}, resume_text)
    with pytest.raises(NotAllowed, match="isn't part"):
        svc.candidate_detail(other.id, top.submission.id)
    assert svc.candidate_detail(campaign.id, top.submission.id).score == 100


def test_campaign_reuses_one_checklist_for_every_student(campaign_setup, resume_text):
    svc, switch, job, campaign = campaign_setup
    _submit(svc, switch, job, "asha", campaign, {"R1": M, "R2": M, "R3": M}, resume_text)
    assert not any(c["step"] == "Read the job" for c in switch.current.calls)


def test_create_campaign_validates_inputs(storage, jd_text):
    from resumemania.ingest import IngestError

    svc = CampaignService(storage, lambda: FakeLLM({}), Models("f", "s"))
    with pytest.raises(IngestError, match="title"):
        svc.create_campaign("", jd_text)
    with pytest.raises(IngestError, match="benchmark"):
        svc.create_campaign("Valid title", jd_text, benchmark=120)
    with pytest.raises(IngestError, match="job description"):
        svc.create_campaign("Valid title", "short")
