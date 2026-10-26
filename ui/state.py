"""Shared app resources, the signed-in user and session keys."""

from __future__ import annotations

import logging

import streamlit as st

from resumemania.agents import Models
from resumemania.config import Settings, load_settings
from resumemania.llm import GeminiLLM
from resumemania.service import CampaignService
from resumemania.storage import Storage

CAMPAIGN_ID = "campaign_id"
RESULT = "student_result"
FLASH = "flash"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@st.cache_resource
def settings() -> Settings:
    return load_settings()


@st.cache_resource
def storage() -> Storage:
    return Storage(settings().db_path)


@st.cache_resource
def llm() -> GeminiLLM:
    s = settings()
    return GeminiLLM(s.require_api_key(), fallback_models=s.fallback_models,
                     timeout_seconds=s.timeout_seconds)


def service() -> CampaignService:
    s = settings()
    # `llm` is resolved lazily, so pages that never call the AI work without an API key.
    return CampaignService(storage(), lambda: llm(), Models(fast=s.fast_model, smart=s.smart_model))


def flash(message: str) -> None:
    """Show a confirmation on the next render ("every screen confirms the last step")."""
    st.session_state[FLASH] = message


def show_flash() -> None:
    message = st.session_state.pop(FLASH, None)
    if message:
        st.success(message)
