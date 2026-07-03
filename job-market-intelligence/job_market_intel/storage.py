from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from .errors import NoRawDataError
from .models import JobPosting, RawResult, ScoreResult


class Workspace:
    def __init__(self, root: Path | str = ".") -> None:
        self.root = Path(root).resolve()
        self.data_dir = self.root / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.reports_dir = self.root / "reports"
        self.db_path = self.data_dir / "job_market.sqlite"

    def ensure_dirs(self) -> None:
        for path in [self.data_dir, self.raw_dir, self.processed_dir, self.reports_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        self.ensure_dirs()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        init_db(conn)
        return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS raw_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            mode TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            raw_path TEXT NOT NULL,
            item_count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS normalized_jobs (
            fingerprint TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            external_id TEXT NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            location TEXT,
            employment_type TEXT,
            experience_min INTEGER,
            experience_max INTEGER,
            education TEXT,
            salary_text TEXT,
            posted_at TEXT,
            deadline_at TEXT,
            description TEXT,
            skills_raw TEXT,
            collected_at TEXT,
            industry TEXT,
            company_type TEXT
        );

        CREATE TABLE IF NOT EXISTS scored_jobs (
            fingerprint TEXT PRIMARY KEY,
            fit_score REAL NOT NULL,
            priority TEXT NOT NULL,
            score_breakdown TEXT NOT NULL,
            skill_gap TEXT NOT NULL,
            matched_projects TEXT NOT NULL,
            resume_bullets TEXT NOT NULL,
            scored_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def item_count(payload: dict[str, Any]) -> int:
    jobs = payload.get("jobs")
    if isinstance(jobs, list):
        return len(jobs)
    if isinstance(jobs, dict):
        job = jobs.get("job", [])
        return len(job) if isinstance(job, list) else int(bool(job))
    return 0


def write_raw_result(workspace: Workspace, result: RawResult) -> Path:
    workspace.ensure_dirs()
    provider_dir = workspace.raw_dir / result.provider
    provider_dir.mkdir(parents=True, exist_ok=True)
    safe_ts = result.fetched_at.replace(":", "").replace("+", "Z")
    raw_path = provider_dir / f"{safe_ts}.json"
    wrapper = {
        "provider": result.provider,
        "mode": result.mode,
        "fetched_at": result.fetched_at,
        "payload": result.payload,
    }
    raw_path.write_text(json.dumps(wrapper, ensure_ascii=False, indent=2), encoding="utf-8")
    with workspace.connect() as conn:
        conn.execute(
            """
            INSERT INTO raw_runs(provider, mode, fetched_at, raw_path, item_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (result.provider, result.mode, result.fetched_at, str(raw_path), item_count(result.payload)),
        )
        conn.commit()
    return raw_path


def load_latest_raw_results(workspace: Workspace, provider: str | None = None) -> list[dict[str, Any]]:
    with workspace.connect() as conn:
        rows = conn.execute(
            """
            SELECT provider, fetched_at, raw_path
            FROM raw_runs
            WHERE (? IS NULL OR provider = ?)
            ORDER BY fetched_at DESC, id DESC
            """,
            (provider, provider),
        ).fetchall()
    latest: dict[str, sqlite3.Row] = {}
    for row in rows:
        latest.setdefault(str(row["provider"]), row)
    if not latest:
        raise NoRawDataError("No raw API responses found. Run collect or demo first.")
    payloads = []
    for row in latest.values():
        payloads.append(json.loads(Path(str(row["raw_path"])).read_text(encoding="utf-8")))
    return payloads


def replace_normalized_jobs(workspace: Workspace, jobs: list[JobPosting]) -> None:
    with workspace.connect() as conn:
        conn.execute("DELETE FROM normalized_jobs")
        conn.executemany(
            """
            INSERT OR REPLACE INTO normalized_jobs(
                fingerprint, source, external_id, company, title, url, location,
                employment_type, experience_min, experience_max, education, salary_text,
                posted_at, deadline_at, description, skills_raw, collected_at, industry,
                company_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    job.fingerprint,
                    job.source,
                    job.external_id,
                    job.company,
                    job.title,
                    job.url,
                    job.location,
                    job.employment_type,
                    job.experience_min,
                    job.experience_max,
                    job.education,
                    job.salary_text,
                    job.posted_at,
                    job.deadline_at,
                    job.description,
                    json.dumps(job.skills_raw, ensure_ascii=False),
                    job.collected_at,
                    job.industry,
                    job.company_type,
                )
                for job in jobs
            ],
        )
        conn.commit()


def fetch_normalized_jobs(workspace: Workspace) -> list[JobPosting]:
    with workspace.connect() as conn:
        rows = conn.execute("SELECT * FROM normalized_jobs ORDER BY source, company, title").fetchall()
    return [_row_to_job(row) for row in rows]


def replace_scored_jobs(workspace: Workspace, results: list[ScoreResult], scored_at: str) -> None:
    with workspace.connect() as conn:
        conn.execute("DELETE FROM scored_jobs")
        conn.executemany(
            """
            INSERT OR REPLACE INTO scored_jobs(
                fingerprint, fit_score, priority, score_breakdown, skill_gap,
                matched_projects, resume_bullets, scored_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    result.job.fingerprint,
                    result.fit_score,
                    result.priority,
                    json.dumps(result.score_breakdown, ensure_ascii=False),
                    json.dumps(result.skill_gap, ensure_ascii=False),
                    json.dumps(result.matched_projects, ensure_ascii=False),
                    json.dumps(result.resume_bullets, ensure_ascii=False),
                    scored_at,
                )
                for result in results
            ],
        )
        conn.commit()


def fetch_scored_jobs(workspace: Workspace) -> list[dict[str, Any]]:
    jobs = {job.fingerprint: job for job in fetch_normalized_jobs(workspace)}
    with workspace.connect() as conn:
        rows = conn.execute("SELECT * FROM scored_jobs ORDER BY fit_score DESC").fetchall()
    records: list[dict[str, Any]] = []
    for row in rows:
        job = jobs[str(row["fingerprint"])]
        data = job.as_dict()
        data.update(
            {
                "fit_score": float(row["fit_score"]),
                "priority": str(row["priority"]),
                "score_breakdown": json.loads(str(row["score_breakdown"])),
                "skill_gap": json.loads(str(row["skill_gap"])),
                "matched_projects": json.loads(str(row["matched_projects"])),
                "resume_bullets": json.loads(str(row["resume_bullets"])),
            }
        )
        records.append(data)
    return records


def row_counts(workspace: Workspace) -> dict[str, int]:
    with workspace.connect() as conn:
        raw_total = conn.execute("SELECT COALESCE(SUM(item_count), 0) AS n FROM raw_runs").fetchone()["n"]
        latest_by_provider: defaultdict[str, int] = defaultdict(int)
        for row in conn.execute("SELECT provider, item_count FROM raw_runs ORDER BY fetched_at DESC, id DESC"):
            latest_by_provider.setdefault(str(row["provider"]), int(row["item_count"]))
        normalized = conn.execute("SELECT COUNT(*) AS n FROM normalized_jobs").fetchone()["n"]
        scored = conn.execute("SELECT COUNT(*) AS n FROM scored_jobs").fetchone()["n"]
    return {
        "raw_total_items": int(raw_total),
        "raw_latest_items": int(sum(latest_by_provider.values())),
        "normalized_jobs": int(normalized),
        "scored_jobs": int(scored),
    }


def _row_to_job(row: sqlite3.Row) -> JobPosting:
    return JobPosting(
        source=str(row["source"]),
        external_id=str(row["external_id"]),
        company=str(row["company"]),
        title=str(row["title"]),
        url=str(row["url"]),
        location=str(row["location"] or ""),
        employment_type=str(row["employment_type"] or ""),
        experience_min=row["experience_min"],
        experience_max=row["experience_max"],
        education=str(row["education"] or ""),
        salary_text=str(row["salary_text"] or ""),
        posted_at=str(row["posted_at"] or ""),
        deadline_at=str(row["deadline_at"] or ""),
        description=str(row["description"] or ""),
        skills_raw=json.loads(str(row["skills_raw"] or "[]")),
        collected_at=str(row["collected_at"] or ""),
        industry=str(row["industry"] or ""),
        company_type=str(row["company_type"] or ""),
    )
