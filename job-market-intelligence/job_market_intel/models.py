from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


STANDARD_FIELDS = [
    "source",
    "external_id",
    "company",
    "title",
    "url",
    "location",
    "employment_type",
    "experience_min",
    "experience_max",
    "education",
    "salary_text",
    "posted_at",
    "deadline_at",
    "description",
    "skills_raw",
    "collected_at",
]


@dataclass(frozen=True)
class RawResult:
    provider: str
    mode: str
    payload: dict[str, Any]
    fetched_at: str


@dataclass(frozen=True)
class JobPosting:
    source: str
    external_id: str
    company: str
    title: str
    url: str
    location: str = ""
    employment_type: str = ""
    experience_min: int | None = None
    experience_max: int | None = None
    education: str = ""
    salary_text: str = ""
    posted_at: str = ""
    deadline_at: str = ""
    description: str = ""
    skills_raw: list[str] = field(default_factory=list)
    collected_at: str = ""
    industry: str = ""
    company_type: str = ""

    @property
    def fingerprint(self) -> str:
        identity = self.url or self.external_id
        normalized = f"{self.company}|{self.title}|{identity}".lower()
        return " ".join(normalized.split())

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NormalizationResult:
    raw_items: int
    filtered_items: int
    deduped_items: int
    duplicate_items: int
    jobs: list[JobPosting]


@dataclass(frozen=True)
class ScoreResult:
    job: JobPosting
    fit_score: float
    priority: str
    score_breakdown: dict[str, float]
    skill_gap: list[str]
    matched_projects: list[dict[str, Any]]
    resume_bullets: list[str]

    def as_dict(self) -> dict[str, Any]:
        data = self.job.as_dict()
        data.update(
            {
                "fit_score": self.fit_score,
                "priority": self.priority,
                "score_breakdown": self.score_breakdown,
                "skill_gap": self.skill_gap,
                "matched_projects": self.matched_projects,
                "resume_bullets": self.resume_bullets,
            }
        )
        return data


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
