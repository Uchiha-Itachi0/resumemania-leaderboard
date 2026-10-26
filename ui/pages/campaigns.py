"""Coordinator: create campaigns and see the ones you run."""

from __future__ import annotations

import streamlit as st

from resumemania.ingest import IngestError
from resumemania.llm import LLMError
from resumemania.ranking import DEFAULT_BENCHMARK
from resumemania.weighted import COMPONENT_LABELS, DEFAULT_WEIGHTS
from ui import copy, state
from ui.components import esc, html, page_title, pill
from ui.report_view import setup_card


def _create_form() -> None:
    with st.expander(copy.NEW_CAMPAIGN, expanded=not state.service().campaigns()):
        if not state.settings().has_api_key:
            setup_card()
            return
        with st.form("new_campaign"):
            left, right = st.columns(2)
            title = left.text_input(copy.CAMP_TITLE, placeholder=copy.CAMP_TITLE_HINT)
            cohort = right.text_input(copy.CAMP_COHORT, placeholder=copy.CAMP_COHORT_HINT)
            jd = st.text_area(copy.CAMP_JD, placeholder=copy.CAMP_JD_HINT, height=240)
            benchmark = st.slider(copy.CAMP_BENCHMARK, 0, 100, DEFAULT_BENCHMARK, step=5, format="%d%%")
            st.caption(copy.CAMP_WEIGHTS)
            cols = st.columns(len(DEFAULT_WEIGHTS))
            weights = {
                key: col.number_input(COMPONENT_LABELS[key], 0, 100, default, step=5, key=f"w_{key}")
                for col, (key, default) in zip(cols, DEFAULT_WEIGHTS.items(), strict=True)
            }
            st.caption(copy.CAMP_PRIVACY)
            submitted = st.form_submit_button(copy.CTA_COORD, type="primary", use_container_width=True)
        if submitted:
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
    svc = state.service()
    dash = svc.dashboard(campaign.id)
    with st.container(border=True):
        left, right = st.columns([3, 1], vertical_alignment="center")
        cohort = f" · {esc(campaign.cohort)}" if campaign.cohort else ""
        left.markdown(
            f"<h3 style='margin:0;font-size:22px'>{esc(campaign.title)}</h3>"
            f"<div class='rm-muted' style='margin-top:6px'>Benchmark {campaign.benchmark}%{cohort}</div>"
            f"<div style='display:flex;gap:6px;margin-top:10px;flex-wrap:wrap'>"
            f"{pill(f'{dash.submitted} resumes', 'mono')}"
            f"{pill(f'{len(dash.candidates)} at benchmark', 'good')}</div>",
            unsafe_allow_html=True,
        )
        if right.button(copy.OPEN_DASHBOARD, key=f"open_{campaign.id}", use_container_width=True):
            st.session_state[state.CAMPAIGN_ID] = campaign.id
            st.switch_page("ui/pages/dashboard.py")


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
