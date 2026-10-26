"""Coordinator dashboard: counts, score spread, ranked candidates, problems, checklist."""

from __future__ import annotations

import csv
import io

import streamlit as st

from resumemania.service import Dashboard, NotAllowed
from ui import copy, report_view, state
from ui.components import esc, html, page_title, pill, stat_tile
from ui.picker import pick_campaign, share_control


def _pick_campaign():
    chosen = pick_campaign()
    if chosen is None:
        st.info(copy.NO_CAMPAIGNS)
        if st.button(copy.CTA_COORD, type="primary"):
            st.switch_page("ui/pages/campaigns.py")
    return chosen


def _tiles(dash: Dashboard) -> None:
    public = sum(1 for c in dash.candidates if c.on_public_board)
    tiles = [
        stat_tile(copy.TILE_SUBMITTED, str(dash.submitted)),
        stat_tile("Not ranked", str(dash.submitted - len(dash.candidates)), sub="Below the bar or unreadable"),
        stat_tile(copy.TILE_ELIGIBLE, str(len(dash.candidates)), f"of {dash.submitted}",
                  bar=(len(dash.candidates) / dash.submitted) if dash.submitted else 0),
        stat_tile(copy.TILE_PUBLIC, str(public),
                  sub=copy.TILE_PUBLIC_SUB.format(label=copy.SHARE_OPTIONS[dash.campaign.public_share])),
    ]
    for col, tile in zip(st.columns(4, gap="small"), tiles, strict=True):
        with col:
            html(tile)


def _share_control(dash: Dashboard) -> None:
    _, changed = share_control(st.selectbox, dash.campaign, key=f"share_{dash.campaign.id}",
                               format_func=copy.SHARE_OPTIONS.get)
    if changed:
        chosen = st.session_state[f"share_{dash.campaign.id}"]
        state.flash(copy.SHARE_SAVED.format(label=copy.SHARE_OPTIONS[chosen].lower()))
        st.rerun()


def _distribution(dash: Dashboard) -> None:
    peak = max(dash.distribution.values()) or 1
    bars = "".join(
        f"<div style='display:flex;flex-direction:column;align-items:center;gap:6px;flex:1'>"
        f"<span style='font-weight:700'>{count}</span>"
        f"<span style='width:100%;height:{max(6, 140 * count // peak)}px;border-radius:10px 10px 4px 4px;"
        f"background:{'var(--lime)' if int(band.split('-')[0]) >= dash.campaign.benchmark else 'var(--sand-2)'}'></span>"
        f"<span class='rm-label'>{band}</span></div>"
        for band, count in dash.distribution.items()
    )
    with st.container(border=True):
        html(f"<div class='rm-label'>{copy.DIST_TITLE}</div><div style='display:flex;align-items:flex-end;"
             f"gap:10px;height:200px;margin-top:14px'>{bars}</div>"
             f"<p class='rm-muted' style='margin:10px 0 0'>{copy.DIST_NOTE}</p>")


def _ranked(dash: Dashboard) -> None:
    html(f"<h3 style='margin:28px 0 4px;font-size:26px'>{copy.RANKED_TITLE}</h3>"
         f"<p class='rm-muted'>{copy.RANKED_NOTE}</p>")
    if not dash.candidates:
        st.info(copy.RANKED_EMPTY)
        return
    for cand in dash.candidates:
        with st.container(border=True):
            cols = st.columns([0.6, 3, 1, 1.4], vertical_alignment="center")
            cols[0].markdown(f"<span class='rm-num' style='width:32px;height:32px'>{cand.rank}</span>",
                             unsafe_allow_html=True)
            badge = pill(copy.BADGE_PUBLIC, "good") if cand.on_public_board else pill(copy.BADGE_PRIVATE, "mono")
            cols[1].markdown(f"<strong style='font-size:17px'>@{esc(cand.github_username)}</strong> {badge}"
                             f"<div class='rm-muted'>Required skills {round(cand.required_component * 100)}%</div>",
                             unsafe_allow_html=True)
            cols[2].markdown(f"<span style='font-family:var(--display);font-size:30px;font-weight:800;"
                             f"letter-spacing:-.04em'>{cand.score}%</span>", unsafe_allow_html=True)
            if cols[3].toggle("Show evidence", key=f"ev_{cand.submission_id}"):
                _candidate(dash, cand.submission_id)


def _candidate(dash: Dashboard, submission_id: int) -> None:
    try:
        evaluation = state.service().candidate_detail(dash.campaign.id, submission_id)
    except NotAllowed as exc:
        st.error(str(exc))
        return
    report_view.breakdown(evaluation.breakdown)
    if evaluation.analysis:
        report_view.requirements(evaluation.analysis)


def _problems(dash: Dashboard) -> None:
    if not dash.problems:
        return
    html(f"<h3 style='margin:28px 0 4px;font-size:22px'>{copy.PROBLEMS_TITLE}</h3>"
         f"<p class='rm-muted'>{copy.PROBLEMS_NOTE}</p>")
    with st.container(border=True):
        html("".join(f"<div class='rm-check'><strong>@{esc(name)}</strong><div class='d'>{esc(reason)}</div></div>"
                     for name, reason in dash.problems))


def _export(dash: Dashboard) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["rank", "github", "score", "required_skills_pct", "public"])
    for c in dash.candidates:
        writer.writerow([c.rank, c.github_username, c.score, round(c.required_component * 100), c.on_public_board])
    st.download_button(copy.EXPORT, buffer.getvalue(), file_name=f"campaign-{dash.campaign.id}-ranked.csv",
                       mime="text/csv")


def render() -> None:
    state.show_flash()
    campaign = _pick_campaign()
    if campaign is None:
        return
    dash = state.service().dashboard(campaign.id)
    page_title(copy.DASH_EYEBROW.format(cohort=campaign.cohort or "All students"),
               copy.DASH_TITLE.format(title=esc(campaign.title)),
               copy.DASH_SUB.format(benchmark=campaign.benchmark))
    html("<div style='height:18px'></div>")
    if dash.submitted == 0:
        st.info(copy.DASH_EMPTY)
        with st.expander(copy.CHECKLIST_TITLE, expanded=True):
            _checklist(campaign)
        return
    _tiles(dash)
    _share_control(dash)
    html("<div style='height:16px'></div>")
    _distribution(dash)
    _ranked(dash)
    _problems(dash)
    html("<div style='height:16px'></div>")
    _export(dash)
    with st.expander(copy.CHECKLIST_TITLE):
        _checklist(campaign)


def _checklist(campaign) -> None:
    for req in campaign.job.requirements:
        st.markdown(f"**{req.id}** {req.text} · _{copy.NEED_TEXT[req.priority.value]}, {req.category.value}_")


render()
