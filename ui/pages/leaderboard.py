"""Public leaderboard: the campaign's top share of eligible students only, nothing about anyone else."""

from __future__ import annotations

import streamlit as st

from resumemania import github
from ui import copy, state
from ui.components import avatar, esc, html, page_title
from ui.picker import pick_campaign
from ui.resume_view import resume_html


def render() -> None:
    state.show_flash()
    campaign = pick_campaign()
    if campaign is None:
        page_title("Leaderboard", "The <em>leaderboard.</em>", copy.NO_CAMPAIGN_YET)
        return
    svc = state.service()
    rows, eligible = svc.leaderboard(campaign.id)
    submitted = svc.dashboard(campaign.id).submitted
    share = campaign.public_share
    title = copy.BOARD_TITLE_ALL if share >= 1 else copy.BOARD_TITLE.format(share=copy.SHARE_SHORT[share])
    page_title(copy.BOARD_EYEBROW.format(title=campaign.title), title,
               copy.BOARD_SUB.format(eligible=eligible, submitted=submitted, benchmark=campaign.benchmark,
                                     share=copy.SHARE_SHORT[share], shown=len(rows)))
    html("<div style='height:18px'></div>")
    if not rows:
        st.info(copy.BOARD_EMPTY)
        return
    for row in rows:
        with st.container(border=True):
            html(
                f"<div style='display:flex;align-items:center;gap:16px'>"
                f"<span class='rm-num' style='width:40px;height:40px;font-size:16px'>{row.rank}</span>"
                f"{avatar(row.github_username, github.avatar_url(row.github_username))}"
                f"<a href='https://github.com/{esc(row.github_username)}' target='_blank' rel='noopener' "
                f"style='font-size:20px;font-weight:700;flex:1;color:var(--ink);text-decoration:none'>"
                f"@{esc(row.github_username)}</a>"
                f"<span style='font-family:var(--display);font-size:34px;font-weight:800;letter-spacing:-.04em'>"
                f"{row.score}%</span></div>"
            )
            if row.shared_resume:
                with st.expander(copy.SEE_RESUME):
                    html(resume_html(row.shared_resume, row.github_username))


render()
