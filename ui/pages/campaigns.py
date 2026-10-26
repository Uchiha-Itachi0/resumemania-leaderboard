"""Coordinator: create campaigns and see the ones that exist."""

from __future__ import annotations

import streamlit as st

from resumemania.ingest import IngestError
from resumemania.llm import LLMError
from resumemania.ranking import DEFAULT_BENCHMARK
from resumemania.weighted import DEFAULT_WEIGHTS, WEIGHT_TOTAL
from ui import copy, state
from ui.components import esc, html, page_title, pill
from ui.report_view import setup_card


def _weights() -> dict[str, int]:
    """Five weight boxes with short labels, help text and a live total."""
    html(f"<div class='rm-label' style='margin-top:10px'>{copy.WEIGHTS_TITLE}</div>"
         f"<p class='rm-muted' style='margin:4px 0 10px'>{copy.WEIGHTS_SUB}</p>")
    cols = st.columns(len(DEFAULT_WEIGHTS), gap="small")
    weights = {}
    for col, (key, default) in zip(cols, DEFAULT_WEIGHTS.items(), strict=True):
        label, help_text = copy.WEIGHT_FIELDS[key]
        weights[key] = int(col.number_input(label, 0, 100, default, step=5, key=f"w_{key}", help=help_text))
    total = sum(weights.values())
    ok = total == WEIGHT_TOTAL
    text = (copy.WEIGHTS_OK if ok else copy.WEIGHTS_BAD).format(total=total)
    html(f"<span class='rm-total {'ok' if ok else 'bad'}'>{esc(text)}</span>")
    return weights


def _create_form() -> None:
    with st.expander(copy.NEW_CAMPAIGN, expanded=not state.service().campaigns()):
        if not state.settings().has_api_key:
            setup_card()
            return
        left, right = st.columns(2)
        title = left.text_input(copy.CAMP_TITLE, placeholder=copy.CAMP_TITLE_HINT, key="camp_title")
        cohort = right.text_input(copy.CAMP_COHORT, placeholder=copy.CAMP_COHORT_HINT, key="camp_cohort")
        jd = st.text_area(copy.CAMP_JD, placeholder=copy.CAMP_JD_HINT, height=220, key="camp_jd")
        benchmark = st.slider(copy.CAMP_BENCHMARK, 0, 100, DEFAULT_BENCHMARK, step=5, format="%d%%",
                              help=copy.CAMP_BENCHMARK_HELP, key="camp_benchmark")
        weights = _weights()
        st.caption(copy.CAMP_PRIVACY)
        ready = sum(weights.values()) == WEIGHT_TOTAL
        if st.button(copy.CTA_COORD, type="primary", use_container_width=True, disabled=not ready):
            _create(title, jd, cohort, benchmark, weights)


def _create(title: str, jd: str, cohort: str, benchmark: int, weights: dict[str, int]) -> None:
    try:
        with st.spinner(copy.CAMP_CREATING):
            campaign = state.service().create_campaign(title, jd, cohort, benchmark, weights)
    except (IngestError, LLMError, ValueError) as exc:
        st.error(str(exc))
        return
    st.session_state[state.CAMPAIGN_ID] = campaign.id
    state.flash(copy.CAMP_CREATED.format(title=campaign.title))
    st.switch_page("ui/pages/dashboard.py")


def _campaign_card(campaign) -> None:
    dash = state.service().dashboard(campaign.id)
    with st.container(border=True):
        left, right = st.columns([3, 1], vertical_alignment="center")
        cohort = f" · {esc(campaign.cohort)}" if campaign.cohort else ""
        with left:
            html(
                f"<div style='display:flex;flex-direction:column;gap:6px;padding:2px 0 6px'>"
                f"<span style='font-family:var(--display);font-size:22px;font-weight:700;letter-spacing:-.03em'>"
                f"{esc(campaign.title)}</span>"
                f"<span class='rm-muted'>Benchmark {campaign.benchmark}%{cohort}</span>"
                f"<span style='display:flex;gap:6px;flex-wrap:wrap;margin-top:4px'>"
                f"{pill(_plural(dash.submitted, 'resume'), 'mono')}{pill(f'{len(dash.candidates)} at benchmark', 'good')}"
                f"</span></div>"
            )
        if right.button(copy.OPEN_DASHBOARD, key=f"open_{campaign.id}", use_container_width=True):
            st.session_state[state.CAMPAIGN_ID] = campaign.id
            st.switch_page("ui/pages/dashboard.py")


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def render() -> None:
    state.show_flash()
    page_title("Campaigns", copy.CAMPAIGNS_TITLE, copy.CAMPAIGNS_SUB)
    html("<div style='height:18px'></div>")
    _create_form()
    campaigns = state.service().campaigns()
    if not campaigns:
        st.info(copy.NO_CAMPAIGNS)
    for campaign in campaigns:
        _campaign_card(campaign)


render()
