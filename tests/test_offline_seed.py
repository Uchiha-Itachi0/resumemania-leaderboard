"""The offline stand-in used for demo data must work with the real service and make no AI calls."""

from __future__ import annotations

from pathlib import Path

from resumemania.agents import Models
from resumemania.ingest import extract_text
from resumemania.schemas import Category, JobRequirements, Priority, Requirement
from resumemania.service import CampaignService
from scripts.offline_llm import OfflineLLM

RESUMES = Path(__file__).resolve().parent.parent / "samples" / "resumes"


def test_offline_seed_ranks_best_fit_first(storage, jd_text):
    job = JobRequirements(requirements=[
        Requirement(id="R1", text="SQL", priority=Priority.MUST, keywords=["SQL"]),
        Requirement(id="R2", text="Power BI or Tableau", priority=Priority.MUST, keywords=["Power BI", "Tableau"]),
        Requirement(id="R3", text="A/B testing", priority=Priority.NICE, keywords=["A/B test"]),
        Requirement(id="R4", text="Degree", priority=Priority.NICE, category=Category.EDUCATION,
                    keywords=["Computer Engineering"]),
    ])
    offline = OfflineLLM()
    svc = CampaignService(storage, lambda: offline, Models("f", "s"))
    campaign = storage.create_campaign("Data Analyst", jd_text, job, "", 60, {"required": 40, "evidence": 25,
                                       "experience": 15, "preferred": 10, "education": 10})
    results = {}
    for name in ("aarav-mehta-data-analyst.pdf", "kabir-malhotra-frontend.pdf", "arjun-nair-fullstack.docx"):
        path = RESUMES / name
        results[name] = svc.submit(campaign.id, extract_text(name, path.read_bytes(), 5), consent=True)

    aarav = results["aarav-mehta-data-analyst.pdf"]
    assert aarav.rank == 1 and aarav.evaluation.status == "eligible"
    assert aarav.submission.github_username == "aarav-mehta-data"
    assert aarav.evaluation.analysis.resume.name == "Aarav Mehta"
    assert results["kabir-malhotra-frontend.pdf"].evaluation.status in ("below", "irrelevant")
    assert offline.calls > 0  # the stand-in answered every agent call; no network involved
