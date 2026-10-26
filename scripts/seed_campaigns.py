"""Create the ten sample campaigns from samples/jds/ using your Gemini key.

    python scripts/seed_campaigns.py

Each job description is read once by the AI. Campaigns that already exist (same title)
are skipped, so it is safe to run twice.
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from resumemania.agents import Models  # noqa: E402
from resumemania.config import load_settings  # noqa: E402
from resumemania.llm import GeminiLLM  # noqa: E402
from resumemania.service import CampaignService  # noqa: E402
from resumemania.storage import Storage  # noqa: E402

CAMPAIGNS = (
    ("01-data-analyst-intern.txt", "Data Analyst Intern", "CSE and IT, batch 2026", 60),
    ("02-ai-engineer.txt", "AI Engineer (Fresher)", "All branches, batch 2026", 65),
    ("03-frontend-react.txt", "Frontend Developer, React", "CSE and IT, batch 2026", 60),
    ("04-backend-java.txt", "Backend Engineer, Java", "CSE, batch 2026", 60),
    ("05-ml-engineer-recsys.txt", "ML Engineer, Recommendations", "M.Sc. and B.Tech, batch 2026", 70),
    ("06-product-analyst.txt", "Product Analyst", "All branches and MBA, batch 2026", 55),
    ("07-cloud-devops-intern.txt", "Cloud and DevOps Intern", "ECE, EEE and CSE, batch 2026", 55),
    ("08-android-developer.txt", "Android Developer, Kotlin", "CSE and IT, batch 2026", 60),
    ("09-fullstack-mern.txt", "Full-Stack Developer, MERN", "All branches, batch 2026", 50),
    ("10-cybersecurity-intern.txt", "Cybersecurity Analyst Intern", "CSE and IT, batch 2026", 60),
)
PARALLEL = 5


def main() -> None:
    settings = load_settings()
    llm = GeminiLLM(settings.require_api_key(), fallback_models=settings.fallback_models,
                    timeout_seconds=settings.timeout_seconds)
    service = CampaignService(Storage(settings.db_path), lambda: llm,
                              Models(fast=settings.fast_model, smart=settings.smart_model))
    existing = {c.title for c in service.campaigns()}
    todo = [c for c in CAMPAIGNS if c[1] not in existing]

    def create(entry: tuple[str, str, str, int]) -> str:
        file, title, cohort, benchmark = entry
        jd = (ROOT / "samples" / "jds" / file).read_text()
        campaign = service.create_campaign(title, jd, cohort, benchmark)
        return f"created  {title} ({len(campaign.job.requirements)} requirements, benchmark {benchmark}%)"

    for title in sorted(existing & {c[1] for c in CAMPAIGNS}):
        print(f"skipped  {title} (already exists)")
    with ThreadPoolExecutor(PARALLEL) as pool:
        for line in pool.map(create, todo):
            print(line)
    print(f"Database: {settings.db_path}")


if __name__ == "__main__":
    main()
