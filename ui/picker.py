"""Campaign picker shared by every page. Remembers the choice across pages."""

from __future__ import annotations

import streamlit as st

from . import copy, state


def pick_campaign(label: str = copy.PICK_CAMPAIGN):
    campaigns = state.service().campaigns()
    if not campaigns:
        return None
    ids = [c.id for c in campaigns]
    current = st.session_state.get(state.CAMPAIGN_ID)
    chosen = st.selectbox(label, campaigns, index=ids.index(current) if current in ids else 0,
                          format_func=lambda c: f"{c.title} · {c.cohort}" if c.cohort else c.title)
    st.session_state[state.CAMPAIGN_ID] = chosen.id
    return chosen
