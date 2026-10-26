"""Public leaderboard: top 10% of eligible students only, nothing about anyone else."""

from __future__ import annotations

import streamlit as st

from resumemania import github
from ui import copy, state
from ui.components import esc, html, page_title
from ui.picker import pick_campaign


def render() -> None:
    state.show_flash()
    campaign = pick_campaign()
    if campaign is None:
        page_title("Leaderboard", copy.BOARD_TITLE, copy.NO_CAMPAIGN_YET)
        return
    rows, eligible = state.service().leaderboard(campaign.id)
    page_title(copy.BOARD_EYEBROW.format(title=campaign.title), copy.BOARD_TITLE,
               copy.BOARD_SUB.format(eligible=eligible, benchmark=campaign.benchmark, shown=len(rows)))
    html("<div style='height:18px'></div>")
    if not rows:
        st.info(copy.BOARD_EMPTY)
        return
    for row in rows:
        with st.container(border=True):
            html(
                f"<div style='display:flex;align-items:center;gap:16px'>"
                f"<span class='rm-num' style='width:40px;height:40px;font-size:16px'>{row.rank}</span>"
                f"<img src='{esc(github.avatar_url(row.github_username))}' alt='' width='44' height='44' "
                f"style='border-radius:999px;border:1px solid var(--line)'>"
                f"<a href='https://github.com/{esc(row.github_username)}' target='_blank' rel='noopener' "
                f"style='font-size:20px;font-weight:700;flex:1;color:var(--ink);text-decoration:none'>"
                f"@{esc(row.github_username)}</a>"
                f"<span style='font-family:var(--display);font-size:34px;font-weight:800;letter-spacing:-.04em'>"
                f"{row.score}%</span></div>"
            )
            if row.shared_resume:
                with st.expander(copy.SEE_RESUME):
                    st.text(row.shared_resume)


render()
