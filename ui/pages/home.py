"""Landing: the promise, one button per audience, how it works, questions."""

from __future__ import annotations

import streamlit as st

from ui import copy, state
from ui.components import esc, hero, html, section_title


def _how_it_works() -> None:
    section_title(copy.HOW_EYEBROW, copy.HOW_TITLE)
    cols = st.columns(3, gap="medium")
    for col, (tag, title, body) in zip(cols, copy.HOW_STEPS, strict=True):
        with col:
            html(f"<article class='rm-step'><span class='rm-tag'>{esc(tag)}</span>"
                 f"<span class='t'>{esc(title)}</span><span class='b'>{esc(body)}</span></article>")
    section_title("Questions", "Before you <em>start.</em>")
    for question, answer in copy.FAQ:
        with st.expander(question):
            st.write(answer)


def render() -> None:
    state.show_flash()
    hero(copy.HERO_BADGE, copy.HERO_TITLE, copy.HERO_SUB, copy.HERO_TICKS)
    _, left, right, _ = st.columns([1, 1.2, 1.2, 1])
    if left.button(copy.CTA_STUDENT, type="primary", use_container_width=True):
        st.switch_page("ui/pages/submit.py")
    if right.button(copy.CTA_COORD, type="tertiary", use_container_width=True):
        st.switch_page("ui/pages/campaigns.py")
    html(f"<p class='rm-muted' style='text-align:center;margin-top:6px'>{copy.HERO_CTA_NOTE}</p>")
    _how_it_works()


render()
