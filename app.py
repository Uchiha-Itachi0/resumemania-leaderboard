"""ResumeMania Leaderboard. Run with:  streamlit run app.py"""

from __future__ import annotations

import streamlit as st

from ui import copy
from ui.theme import apply_theme

st.set_page_config(page_title=f"{copy.APP_NAME}: who's ready to place?",
                   page_icon=":material/leaderboard:", layout="wide", initial_sidebar_state="collapsed")
apply_theme()

pages = [
    st.Page("ui/pages/home.py", title="Home", default=True),
    st.Page("ui/pages/submit.py", title=copy.CTA_STUDENT, url_path="check"),
    st.Page("ui/pages/leaderboard.py", title="Leaderboard", url_path="leaderboard"),
    st.Page("ui/pages/campaigns.py", title="Campaigns", url_path="campaigns"),
    st.Page("ui/pages/dashboard.py", title="Dashboard", url_path="dashboard"),
]
st.navigation(pages, position="top").run()
