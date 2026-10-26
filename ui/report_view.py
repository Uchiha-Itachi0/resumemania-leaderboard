"""Report pieces shared by the student page and the coordinator's candidate view."""

from __future__ import annotations

import streamlit as st

from resumemania.schemas import Analysis, MatchStatus

from . import copy
from .components import CHECK_SVG, chips, esc, html, pill, with_marks


def setup_card() -> None:
    steps = "".join(f"<li><span class='rm-num'>{i}</span><span>{step}</span></li>"
                    for i, step in enumerate(copy.SETUP_STEPS, 1))
    html(f"<article class='rm-dark' style='margin:20px 0'><span class='rm-label'>Setup</span>"
         f"<h3>{copy.SETUP_TITLE}</h3><p>{copy.SETUP_BODY}</p><ol>{steps}</ol></article>")


def breakdown(rows: list[dict]) -> None:
    """Each component's value and its effective weight, as bars."""
    items = []
    for row in rows:
        if row["value"] is None:
            continue
        pct = round(row["value"] * 100)
        weight = round(row["weight"] * 100)
        items.append(
            f"<div style='display:grid;grid-template-columns:minmax(0,1fr) 56px;gap:4px 12px;padding:10px 0;"
            f"border-top:1px solid var(--line)'><span style='font-weight:600'>{esc(row['label'])}"
            f" <span class='rm-muted'>· {weight}% of score</span></span>"
            f"<span style='text-align:right;font-weight:700'>{pct}%</span>"
            f"<span class='rm-bar' style='grid-column:1 / 3'><span style='width:{pct}%'></span></span></div>"
        )
    with st.container(border=True):
        html(f"<div class='rm-label'>{copy.BREAKDOWN_TITLE}</div>" + "".join(items))


def requirements(a: Analysis) -> None:
    rows = []
    for req in a.job.requirements:
        match = a.match_for(req.id)
        status = match.status.value if match else MatchStatus.MISSING.value
        evidence = (
            "".join(f"<div class='ev'>“{esc(q)}”</div>" for q in match.evidence)
            if match and match.evidence else f"<div class='note'>{copy.NO_EVIDENCE}</div>"
        )
        note = f"<div class='note'>{esc(match.note)}</div>" if match and match.note else ""
        rows.append(
            f"<div class='rm-row'><span class='id'>{esc(req.id)}</span><span class='req'>{esc(req.text)}</span>"
            f"<span class='pills'>{pill(copy.NEED_TEXT[req.priority.value], 'mono')}"
            f"{pill(copy.STATUS_TEXT[status], copy.STATUS_CLASS[status])}</span>{evidence}{note}</div>"
        )
    with st.container(border=True):
        html("".join(rows) or "<p class='rm-muted'>Nothing here.</p>")


def plan(a: Analysis) -> None:
    rows = "".join(
        f"<div class='rm-action'><span class='rm-num'>{i}</span><div>"
        f"<div class='t'>{esc(act.title)} {pill(copy.SEVERITY_TEXT[act.priority.value], _sev(act.priority.value))}"
        f"</div><div class='d'>{esc(act.detail)}</div></div></div>"
        for i, act in enumerate(a.plan.actions, 1)
    )
    html(f"<div>{rows}</div>")
    if a.quality.strengths:
        html("<div class='rm-label' style='margin:18px 0 6px'>Already working</div>")
        html("".join(f"<div class='rm-check'>{CHECK_SVG}<span>{esc(s)}</span></div>" for s in a.quality.strengths))
    if a.keywords_missing:
        html("<div class='rm-label' style='margin:18px 0 10px'>Keywords not in the resume yet</div>")
        html(chips(a.keywords_missing))


def rewrites(a: Analysis) -> None:
    if not a.plan.edits:
        st.caption("No rewrites this time.")
        return
    html(f"<p class='rm-muted'>{copy.REWRITES_NOTE}</p>")
    for edit in a.plan.edits:
        with st.container(border=True):
            html(f"<div class='rm-label'>Before</div><div class='rm-before'>{esc(edit.original_text)}</div>")
            html(f"<div class='rm-label' style='margin-top:12px'>Suggested</div>"
                 f"<div class='rm-quote'>{with_marks(edit.proposed_text)}</div>")
            html(f"<p class='rm-muted' style='margin:8px 0 0'>Why: {esc(edit.rationale)}</p>")
            for flag in edit.flags:
                html(f"<div class='rm-flag' style='margin-top:8px'>{with_marks(flag)}</div>")


def _sev(severity: str) -> str:
    return {"high": "miss", "medium": "part", "low": ""}[severity]
