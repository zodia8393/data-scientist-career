from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from .models import JobPosting


ROLE_BUCKETS = {
    "data_scientist": ("data scientist", "데이터 사이언티스트"),
    "product_data_scientist": ("product data", "프로덕트 데이터"),
    "ml_engineer": ("ml engineer", "machine learning engineer", "머신러닝 엔지니어"),
    "applied_ai": ("applied ai", "ai data", "응용 ai"),
    "data_analyst": ("data analyst", "데이터 분석"),
}


def analyze_jobs(jobs: list[JobPosting], today: datetime | None = None) -> dict[str, Any]:
    today = today or datetime.now()
    role_counts = Counter(_role_bucket(job) for job in jobs)
    skill_counts = Counter(skill for job in jobs for skill in job.skills_raw)
    location_counts = Counter(_primary_location(job.location) for job in jobs if job.location)
    industry_counts = Counter(job.industry or "unknown" for job in jobs)
    company_type_counts = Counter(job.company_type or "unknown" for job in jobs)
    experience_counts = Counter(_experience_bucket(job) for job in jobs)
    deadline_soon = [job for job in jobs if _within_window(job.deadline_at, today, past_days=1, future_days=14)]
    recent = [job for job in jobs if _within_window(job.posted_at, today, past_days=14, future_days=1)]
    return {
        "total_jobs": len(jobs),
        "role_counts": dict(role_counts.most_common()),
        "skill_counts": dict(skill_counts.most_common()),
        "location_counts": dict(location_counts.most_common()),
        "industry_counts": dict(industry_counts.most_common()),
        "company_type_counts": dict(company_type_counts.most_common()),
        "experience_counts": dict(experience_counts.most_common()),
        "deadline_soon_count": len(deadline_soon),
        "recent_posting_count": len(recent),
        "deadline_soon_jobs": [_job_ref(job) for job in deadline_soon[:10]],
        "recent_jobs": [_job_ref(job) for job in recent[:10]],
    }


def _role_bucket(job: JobPosting) -> str:
    text = f"{job.title} {job.description}".lower()
    for bucket, keywords in ROLE_BUCKETS.items():
        if any(keyword in text for keyword in keywords):
            return bucket
    return "other_ds_ai"


def _experience_bucket(job: JobPosting) -> str:
    min_years = job.experience_min
    if min_years is None or min_years <= 1:
        return "entry_or_unspecified"
    if min_years <= 4:
        return "mid"
    if min_years <= 8:
        return "senior"
    return "lead"


def _primary_location(location: str) -> str:
    head = location.split(",")[0].split("/")[0].split(">")[0]
    return head.strip() or "unknown"


def _within_window(value: str, today: datetime, past_days: int, future_days: int) -> bool:
    parsed = _parse_datetime(value)
    if parsed is None:
        return False
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    delta = parsed - today.replace(tzinfo=None)
    return timedelta(days=-past_days) <= delta <= timedelta(days=future_days)


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _job_ref(job: JobPosting) -> dict[str, str]:
    return {"company": job.company, "title": job.title, "deadline_at": job.deadline_at, "url": job.url}
