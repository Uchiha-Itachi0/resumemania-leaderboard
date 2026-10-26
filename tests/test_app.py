"""End-to-end UI tests with Streamlit's AppTest. The AI is replaced by FakeLLM."""

from __future__ import annotations

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import ui.state as ui_state
from resumemania.llm import FakeLLM
from resumemania.schemas import (
    Category,
    EvidenceMatch,
    FeedbackPlan,
    JobRequirements,
    MatchResult,
    MatchStatus,
    ParsedResume,
    Priority,
    QualityReview,
    Requirement,
)
from ui import copy

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 30


@pytest.fixture
def fake() -> FakeLLM:
    job = JobRequirements(role_title="Analyst", requirements=[
        Requirement(id="R1", text="Strong SQL", priority=Priority.MUST, category=Category.SKILL, keywords=["SQL"]),
        Requirement(id="R2", text="Python", priority=Priority.MUST, category=Category.SKILL, keywords=["Python"]),
    ])
    matches = [EvidenceMatch(requirement_id=r, status=MatchStatus.MATCHED, where="Experience",
                             evidence=["Cleaned customer data using Python and Pandas."]) for r in ("R1", "R2")]
    return FakeLLM({JobRequirements: job, ParsedResume: ParsedResume(name="Priya Sharma"),
                    MatchResult: MatchResult(matches=matches),
                    QualityReview: QualityReview(strengths=["Clear sections"]), FeedbackPlan: FeedbackPlan()})


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path, fake):
    monkeypatch.setenv("RESUMEMANIA_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("resumemania.config.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ui_state, "llm", lambda: fake)
    st.cache_resource.clear()
    yield
    st.cache_resource.clear()


def _md(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


def _button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


def _create_campaign(at: AppTest, jd_text: str) -> AppTest:
    at.switch_page("ui/pages/campaigns.py").run()
    next(t for t in at.text_input if t.label == copy.CAMP_TITLE).set_value("Data Analyst Intern")
    next(t for t in at.text_area if t.label == copy.CAMP_JD).set_value(jd_text)
    return _button(at, copy.CTA_COORD).click().run()


def test_landing_shows_promise_and_both_ctas():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    assert not at.exception
    assert "ready to place" in _md(at)
    labels = {b.label for b in at.button}
    assert {copy.CTA_STUDENT, copy.CTA_COORD} <= labels


def test_full_flow_campaign_to_leaderboard(jd_text, resume_text):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    _create_campaign(at, jd_text)
    assert not at.exception, at.exception
    assert any("Campaign ready" in s.value for s in at.success)

    at.switch_page("ui/pages/submit.py").run()
    at.text_area(key="resume_paste").set_value(resume_text + "\ngithub.com/priya-s")
    at.checkbox(key="consent").check()
    _button(at, copy.CTA_STUDENT).click().run()
    assert not at.exception, at.exception
    md = _md(at)
    assert "@priya-s" in md and "#1" in md

    at.switch_page("ui/pages/leaderboard.py").run()
    md = _md(at)
    assert "@priya-s" in md and "100%" in md

    at.switch_page("ui/pages/dashboard.py").run()
    assert not at.exception, at.exception
    assert "@priya-s" in _md(at)


def test_github_username_taken_from_resume(jd_text, resume_text):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    _create_campaign(at, jd_text)
    at.switch_page("ui/pages/submit.py").run()
    at.text_area(key="resume_paste").set_value(resume_text + "\ngithub.com/priya-from-resume")
    _button(at, copy.CTA_STUDENT).click().run()
    assert any("priya-from-resume" in s.value for s in at.success)


def test_resume_without_github_link_is_explained(jd_text, resume_text):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    _create_campaign(at, jd_text)
    at.switch_page("ui/pages/submit.py").run()
    at.text_area(key="resume_paste").set_value(resume_text)
    _button(at, copy.CTA_STUDENT).click().run()
    assert any("GitHub profile link" in e.value for e in at.error)
    assert all(t.key != "github" for t in at.text_input)


def test_pages_without_campaigns_point_the_way():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    at.switch_page("ui/pages/submit.py").run()
    assert copy.NO_CAMPAIGN_YET in [i.value for i in at.info]
    at.switch_page("ui/pages/leaderboard.py").run()
    assert not at.exception


def test_weights_must_total_100_before_creating():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    at.switch_page("ui/pages/campaigns.py").run()
    assert not _button(at, copy.CTA_COORD).disabled
    at.number_input(key="w_required").set_value(35).run()
    assert _button(at, copy.CTA_COORD).disabled
    assert "Total 95 of 100" in _md(at)


def test_empty_dashboard_explains_next_step(jd_text):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    _create_campaign(at, jd_text)
    assert copy.DASH_EMPTY in [i.value for i in at.info]
