"""SQLite repository: plain reads and writes. Business rules live in service.py."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .schemas import Analysis, JobRequirements

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    job_description TEXT NOT NULL,
    requirements_json TEXT NOT NULL,
    cohort TEXT NOT NULL DEFAULT '',
    benchmark INTEGER NOT NULL,
    weights_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    github_key TEXT NOT NULL,
    github_username TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 1,
    consent_to_share INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE (campaign_id, github_key)
);
CREATE TABLE IF NOT EXISTS evaluations (
    submission_id INTEGER PRIMARY KEY REFERENCES submissions(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    required_component REAL NOT NULL DEFAULT 0,
    keyword_coverage REAL NOT NULL DEFAULT 0,
    breakdown_json TEXT NOT NULL DEFAULT '[]',
    analysis_json TEXT,
    message TEXT NOT NULL DEFAULT '',
    scoring_version TEXT NOT NULL,
    evaluated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS leaderboard_snapshots (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    generated_at TEXT NOT NULL,
    eligible_ids_json TEXT NOT NULL,
    visible_ids_json TEXT NOT NULL,
    ranking_version TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


@dataclass(frozen=True)
class Campaign:
    id: int
    title: str
    job_description: str
    job: JobRequirements
    cohort: str
    benchmark: int
    weights: dict[str, int]
    created_at: str


@dataclass(frozen=True)
class Submission:
    id: int
    campaign_id: int
    github_username: str
    content: str
    source: str
    page_count: int
    consent_to_share: bool
    created_at: str


@dataclass(frozen=True)
class Evaluation:
    submission_id: int
    status: str
    score: int
    required_component: float
    keyword_coverage: float
    breakdown: list[dict]
    analysis: Analysis | None
    message: str
    scoring_version: str
    evaluated_at: str


@dataclass(frozen=True)
class Snapshot:
    campaign_id: int
    generated_at: str
    eligible_ids: tuple[int, ...]
    visible_ids: tuple[int, ...]
    ranking_version: str


class Storage:
    def __init__(self, db_path: Path):
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- campaigns ----------

    def create_campaign(self, title: str, job_description: str, job: JobRequirements, cohort: str,
                        benchmark: int, weights: dict[str, int]) -> Campaign:
        created = now()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO campaigns (title, job_description, requirements_json, cohort, benchmark,"
                " weights_json, created_at) VALUES (?,?,?,?,?,?,?)",
                (title, job_description, job.model_dump_json(), cohort, benchmark, json.dumps(weights), created),
            )
        return Campaign(cur.lastrowid, title, job_description, job, cohort, benchmark, weights, created)

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        return _campaign(row) if row else None

    def list_campaigns(self) -> list[Campaign]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
        return [_campaign(r) for r in rows]

    # ---------- submissions and evaluations ----------

    def replace_submission(self, campaign_id: int, github_username: str, github_key: str, content: str,
                           source: str, page_count: int, consent: bool) -> Submission:
        """One entry per GitHub user per campaign: a new upload removes the old one and its score."""
        created = now()
        with self._connect() as conn:
            conn.execute("DELETE FROM submissions WHERE campaign_id = ? AND github_key = ?", (campaign_id, github_key))
            cur = conn.execute(
                "INSERT INTO submissions (campaign_id, github_key, github_username, content, source, page_count,"
                " consent_to_share, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (campaign_id, github_key, github_username, content, source, page_count, int(consent), created),
            )
        return Submission(cur.lastrowid, campaign_id, github_username, content, source, page_count, consent, created)

    def get_submission(self, submission_id: int) -> Submission | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
        return _submission(row) if row else None

    def submissions(self, campaign_id: int) -> list[Submission]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM submissions WHERE campaign_id = ? ORDER BY id", (campaign_id,)).fetchall()
        return [_submission(r) for r in rows]

    def save_evaluation(self, evaluation: Evaluation) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO evaluations (submission_id, status, score, required_component,"
                " keyword_coverage, breakdown_json, analysis_json, message, scoring_version, evaluated_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                (evaluation.submission_id, evaluation.status, evaluation.score, evaluation.required_component,
                 evaluation.keyword_coverage, json.dumps(evaluation.breakdown),
                 evaluation.analysis.model_dump_json() if evaluation.analysis else None,
                 evaluation.message, evaluation.scoring_version, evaluation.evaluated_at),
            )

    def get_evaluation(self, submission_id: int) -> Evaluation | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM evaluations WHERE submission_id = ?", (submission_id,)).fetchone()
        return _evaluation(row) if row else None

    # ---------- leaderboard ----------

    def save_snapshot(self, snapshot: Snapshot) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO leaderboard_snapshots (campaign_id, generated_at, eligible_ids_json,"
                " visible_ids_json, ranking_version) VALUES (?,?,?,?,?)",
                (snapshot.campaign_id, snapshot.generated_at, json.dumps(list(snapshot.eligible_ids)),
                 json.dumps(list(snapshot.visible_ids)), snapshot.ranking_version),
            )

    def latest_snapshot(self, campaign_id: int) -> Snapshot | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM leaderboard_snapshots WHERE campaign_id = ? ORDER BY id DESC LIMIT 1",
                (campaign_id,)).fetchone()
        if row is None:
            return None
        return Snapshot(row["campaign_id"], row["generated_at"], tuple(json.loads(row["eligible_ids_json"])),
                        tuple(json.loads(row["visible_ids_json"])), row["ranking_version"])


def _campaign(row: sqlite3.Row) -> Campaign:
    return Campaign(
        id=row["id"], title=row["title"], job_description=row["job_description"],
        job=JobRequirements.model_validate_json(row["requirements_json"]), cohort=row["cohort"],
        benchmark=row["benchmark"], weights=json.loads(row["weights_json"]), created_at=row["created_at"],
    )


def _submission(row: sqlite3.Row) -> Submission:
    return Submission(row["id"], row["campaign_id"], row["github_username"], row["content"], row["source"],
                      row["page_count"], bool(row["consent_to_share"]), row["created_at"])


def _evaluation(row: sqlite3.Row) -> Evaluation:
    analysis = Analysis.model_validate_json(row["analysis_json"]) if row["analysis_json"] else None
    return Evaluation(row["submission_id"], row["status"], row["score"], row["required_component"],
                      row["keyword_coverage"], json.loads(row["breakdown_json"]), analysis, row["message"],
                      row["scoring_version"], row["evaluated_at"])
