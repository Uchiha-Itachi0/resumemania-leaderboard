"""Student: pick a campaign, give a GitHub username and a resume, see a private result."""

from __future__ import annotations

import streamlit as st

from resumemania import github
from resumemania.ingest import IngestError, extract_text, from_paste
from resumemania.service import StudentResult
from ui import copy, report_view, state
from ui.components import esc, html, page_title, stat_tile
from ui.picker import pick_campaign


def _form(campaign) -> None:
    if not state.settings().has_api_key:
        report_view.setup_card()
        return
    max_mb = state.settings().max_upload_mb
    with st.container(border=True):
        username = st.text_input(copy.GITHUB, placeholder=copy.GITHUB_HINT, key="github")
        paste_tab, upload_tab = st.tabs([copy.RESUME_PASTE, copy.RESUME_UPLOAD])
        with paste_tab:
            pasted = st.text_area(copy.RESUME_PASTE_HINT, height=200, label_visibility="collapsed",
                                  placeholder=copy.RESUME_PASTE_HINT, key="resume_paste")
        with upload_tab:
            upload = st.file_uploader(copy.RESUME_UPLOAD, type=["pdf", "docx", "txt"], label_visibility="collapsed")
            st.caption(copy.RESUME_UPLOAD_HELP.format(mb=max_mb))
        consent = st.checkbox(copy.CONSENT, key="consent")
        go = st.button(copy.CTA_STUDENT, type="primary", use_container_width=True)
    if go:
        _run(campaign, username, pasted, upload, consent, max_mb)


def _run(campaign, username: str, pasted: str, upload, consent: bool, max_mb: int) -> None:
    try:
        if upload is not None:
            resume = extract_text(upload.name, upload.getvalue(), max_mb)
        elif pasted.strip():
            resume = from_paste(pasted)
        else:
            st.error(copy.ERR_NEED_RESUME)
            return
        handle = username.strip() or github.from_resume(resume.text)
        if not handle:
            st.error(copy.GITHUB_MISSING)
            return
        with st.spinner(copy.RUNNING):
            result = state.service().submit(campaign.id, handle, resume, consent)
    except (IngestError, github.InvalidUsername) as exc:
        st.error(str(exc))
        return
    st.session_state[state.RESULT] = result
    note = copy.GITHUB_FROM_RESUME.format(username=result.submission.github_username) if not username.strip() else ""
    state.flash(f"{copy.RUN_DONE} {note}".strip())
    st.rerun()


def _result(result: StudentResult) -> None:
    ev = result.evaluation
    head = copy.STATUS_HEAD[ev.status].format(rank=result.rank, total=result.eligible_count, score=ev.score,
                                              benchmark=result.campaign.benchmark)
    html(f"<div class='rm-page-title' style='margin-top:28px'><span class='rm-eyebrow'>Your result · "
         f"@{esc(result.submission.github_username)} · {esc(result.campaign.title)}</span><h1>{head}</h1>"
         f"<p>{esc(ev.message)}</p></div>")
    if ev.status in ("eligible", "below"):
        public = copy.PUBLIC_YES if result.on_public_board else copy.PUBLIC_NO
        tiles = [
            stat_tile("Your score", f"{ev.score}%", sub=f"Benchmark {result.campaign.benchmark}%", bar=ev.score / 100),
            stat_tile("Your rank", f"#{result.rank}" if result.rank else "Not ranked",
                      f"of {result.eligible_count}" if result.rank else "", sub=public if result.rank else ""),
            stat_tile("Keywords found", f"{round(ev.keyword_coverage * 100)}%", bar=ev.keyword_coverage),
        ]
        html("<div style='height:14px'></div>")
        for col, tile in zip(st.columns(3, gap="small"), tiles, strict=True):
            with col:
                html(tile)
        html("<div style='height:14px'></div>")
        report_view.breakdown(ev.breakdown)
    if ev.analysis:
        plan_tab, reqs_tab, edits_tab = st.tabs([copy.PLAN_TITLE, copy.REQS_TITLE, copy.REWRITES_TITLE])
        with plan_tab:
            report_view.plan(ev.analysis)
        with reqs_tab:
            report_view.requirements(ev.analysis)
        with edits_tab:
            report_view.rewrites(ev.analysis)
    st.caption(copy.REUPLOAD_NOTE)


def render() -> None:
    state.show_flash()
    page_title("Check my rank", copy.STUDENT_TITLE, copy.STUDENT_SUB)
    html("<div style='height:18px'></div>")
    campaign = pick_campaign()
    if campaign is None:
        st.info(copy.NO_CAMPAIGN_YET)
        return
    _form(campaign)
    result: StudentResult | None = st.session_state.get(state.RESULT)
    if result and result.campaign.id == campaign.id:
        _result(result)


render()
