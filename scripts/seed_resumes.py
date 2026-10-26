"""Submit every sample resume to every campaign, so dashboards and leaderboards have data.

    python scripts/seed_resumes.py            # offline: no AI calls, a few seconds
    python scripts/seed_resumes.py --live     # real Gemini: about 4 calls per resume per campaign
    python scripts/seed_resumes.py --limit 3  # only the first 3 campaigns

Offline mode uses a keyword-matching stand-in for Gemini (scripts/offline_llm.py), then the
real gate, scoring, ranking and leaderboard code. Good for demo data, not for judging people.
Live mode runs a few at a time and retries anything the AI couldn't finish.
Safe to run again: a resume with the same GitHub link replaces its earlier entry.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from resumemania.agents import Models  # noqa: E402
from resumemania.config import load_settings  # noqa: E402
from resumemania.ingest import ExtractedText, extract_text  # noqa: E402
from resumemania.llm import GeminiLLM  # noqa: E402
from resumemania.service import FAILED, CampaignService  # noqa: E402
from resumemania.storage import Storage  # noqa: E402
from scripts.offline_llm import OfflineLLM  # noqa: E402

PARALLEL = 3
RETRY_PAUSE_SECONDS = 20
MAX_ROUNDS = 3


def _load_resumes() -> list[tuple[str, ExtractedText]]:
    folder = ROOT / "samples" / "resumes"
    return [(p.name, extract_text(p.name, p.read_bytes(), 5)) for p in sorted(folder.iterdir())
            if p.suffix in (".pdf", ".docx")]


def main(limit: int | None, live: bool) -> None:
    settings = load_settings()
    if live:
        llm = GeminiLLM(settings.require_api_key(), fallback_models=settings.fallback_models,
                        timeout_seconds=settings.timeout_seconds)
    else:
        llm = OfflineLLM()
    service = CampaignService(Storage(settings.db_path), lambda: llm,
                              Models(fast=settings.fast_model, smart=settings.smart_model))
    campaigns = service.campaigns()[:limit] if limit else service.campaigns()
    resumes = _load_resumes()
    if not campaigns:
        sys.exit("No campaigns yet. Run scripts/seed_campaigns.py first.")

    jobs = [(c, i, name, resume) for c in campaigns for i, (name, resume) in enumerate(resumes)]
    mode = "live Gemini" if live else "offline, no AI calls"
    print(f"{len(resumes)} resumes x {len(campaigns)} campaigns = {len(jobs)} checks ({mode})", flush=True)
    started = time.time()

    def run(job) -> tuple[tuple, str]:
        campaign, index, name, resume = job
        result = service.submit(campaign.id, resume, consent=index % 2 == 0)
        ev = result.evaluation
        rank = f"#{result.rank}" if result.rank else "-"
        print(f"{campaign.title[:28]:28} {name[:34]:34} {ev.status:10} {ev.score:3}% {rank}", flush=True)
        return job, ev.status

    todo = jobs
    for round_number in range(1, MAX_ROUNDS + 1):
        with ThreadPoolExecutor(PARALLEL) as pool:
            outcomes = list(pool.map(run, todo))
        todo = [job for job, status in outcomes if status == FAILED]
        if not todo:
            break
        print(f"Round {round_number}: {len(todo)} the AI couldn't finish. Retrying in {RETRY_PAUSE_SECONDS}s.",
              flush=True)
        time.sleep(RETRY_PAUSE_SECONDS)

    print(f"Done in {time.time() - started:.0f}s. Still failed: {len(todo)}.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int, default=None, help="Only the first N campaigns")
    parser.add_argument("--live", action="store_true", help="Use real Gemini instead of the offline stand-in")
    args = parser.parse_args()
    main(args.limit, args.live)
