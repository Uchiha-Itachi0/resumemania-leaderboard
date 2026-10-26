"""Campaign picker shared by every page. Remembers the choice across pages.

The widget has a fixed key and no changing `index`, so Streamlit keeps it as the same
widget between runs and one click is enough to switch.
"""

from __future__ import annotations

import streamlit as st

from . import copy, state

PICKER_KEY = "campaign_picker"


def pick_campaign(label: str = copy.PICK_CAMPAIGN):
    campaigns = state.service().campaigns()
    if not campaigns:
        return None
    by_id = {c.id: c for c in campaigns}
    remembered = st.session_state.get(state.CAMPAIGN_ID)
    if st.session_state.get(PICKER_KEY) not in by_id:
        st.session_state[PICKER_KEY] = remembered if remembered in by_id else campaigns[0].id
    chosen_id = st.selectbox(label, list(by_id), key=PICKER_KEY,
                             format_func=lambda cid: _label(by_id[cid]))
    st.session_state[state.CAMPAIGN_ID] = chosen_id
    return by_id[chosen_id]


def remember(campaign_id: int) -> None:
    """Point every page's picker at this campaign (used before switching pages)."""
    st.session_state[state.CAMPAIGN_ID] = campaign_id
    st.session_state.pop(PICKER_KEY, None)


def share_control(widget, campaign, key: str, **kwargs):
    """A public-share picker with a stable key. Saves a change and returns the fresh campaign."""
    if st.session_state.get(key) not in copy.SHARE_OPTIONS:
        st.session_state[key] = campaign.public_share
    chosen = widget(copy.SHARE_LABEL, list(copy.SHARE_OPTIONS), key=key, help=copy.SHARE_HELP, **kwargs)
    if chosen is None or chosen == campaign.public_share:
        return campaign, False
    state.service().set_public_share(campaign.id, chosen)
    return state.service().campaign(campaign.id), True


def _label(campaign) -> str:
    return f"{campaign.title} · {campaign.cohort}" if campaign.cohort else campaign.title
