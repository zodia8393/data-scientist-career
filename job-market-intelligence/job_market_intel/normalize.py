from __future__ import annotations

from typing import Any

from .models import JobPosting, NormalizationResult
from .skills import extract_skills


TARGET_ROLE_KEYWORDS = (
    "data scientist",
    "데이터 사이언티스트",
    "applied ai",
    "ml engineer",
    "machine learning engineer",
    "머신러닝",
    "product data",
    "데이터 분석",
    "data analyst",
    "ai data",
)


def normalize_raw_wrappers(raw_wrappers: list[dict[str, Any]]) -> NormalizationResult:
    raw_jobs: list[JobPosting] = []
    raw_items = 0
    for wrapper in raw_wrappers:
        provider = str(wrapper.get("provider", "unknown"))
        payload = wrapper.get("payload", {})
        jobs = _extract_raw_jobs(payload)
        raw_items += len(jobs)
        for item in jobs:
            job = _normalize_item(item, provider=provider, collected_at=str(wrapper.get("fetched_at", "")))
            if job and _is_target_role(job):
                raw_jobs.append(job)

    deduped: dict[str, JobPosting] = {}
    duplicate_items = 0
    for job in raw_jobs:
        if job.fingerprint in deduped:
            duplicate_items += 1
            continue
        deduped[job.fingerprint] = job

    jobs = sorted(deduped.values(), key=lambda item: (item.company.lower(), item.title.lower()))
    return NormalizationResult(
        raw_items=raw_items,
        filtered_items=len(raw_jobs),
        deduped_items=len(jobs),
        duplicate_items=duplicate_items,
        jobs=jobs,
    )


def _extract_raw_jobs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = payload.get("jobs", [])
    if isinstance(jobs, list):
        return [item for item in jobs if isinstance(item, dict)]
    if isinstance(jobs, dict):
        job = jobs.get("job", [])
        if isinstance(job, dict):
            return [job]
        if isinstance(job, list):
            return [item for item in job if isinstance(item, dict)]
    return []


def _normalize_item(item: dict[str, Any], provider: str, collected_at: str) -> JobPosting | None:
    if _looks_like_standard_fixture(item):
        description = str(item.get("description") or "")
        skills = sorted(set(list(item.get("skills_raw") or []) + extract_skills(description)), key=str.lower)
        return JobPosting(
            source=str(item.get("source") or provider),
            external_id=str(item.get("external_id") or item.get("id") or ""),
            company=str(item.get("company") or ""),
            title=str(item.get("title") or ""),
            url=str(item.get("url") or ""),
            location=str(item.get("location") or ""),
            employment_type=str(item.get("employment_type") or ""),
            experience_min=_as_int(item.get("experience_min")),
            experience_max=_as_int(item.get("experience_max")),
            education=str(item.get("education") or ""),
            salary_text=str(item.get("salary_text") or ""),
            posted_at=str(item.get("posted_at") or ""),
            deadline_at=str(item.get("deadline_at") or ""),
            description=description,
            skills_raw=skills,
            collected_at=collected_at,
            industry=str(item.get("industry") or ""),
            company_type=str(item.get("company_type") or ""),
        )

    if provider == "saramin":
        return _normalize_saramin_item(item, collected_at=collected_at)
    return None


def _normalize_saramin_item(item: dict[str, Any], collected_at: str) -> JobPosting:
    position = _dict(item.get("position"))
    company = _dict(item.get("company"))
    company_detail = _dict(company.get("detail"))
    location = _dict(position.get("location"))
    job_type = _dict(position.get("job-type"))
    industry = _dict(position.get("industry"))
    job_mid = _dict(position.get("job-mid-code"))
    job_code = _dict(position.get("job-code"))
    experience = _dict(position.get("experience-level"))
    education = _dict(position.get("required-education-level"))
    salary = _dict(item.get("salary"))
    keyword = str(item.get("keyword") or "")
    description = " ".join(
        part
        for part in [
            str(position.get("title") or ""),
            keyword,
            str(industry.get("name") or industry or ""),
            str(job_mid.get("name") or ""),
            str(job_code.get("name") or ""),
        ]
        if part
    )
    return JobPosting(
        source="saramin",
        external_id=str(item.get("id") or ""),
        company=str(company_detail.get("name") or company.get("name") or ""),
        title=str(position.get("title") or ""),
        url=str(item.get("url") or ""),
        location=str(location.get("name") or location or ""),
        employment_type=str(job_type.get("name") or job_type or ""),
        experience_min=_as_int(experience.get("min")),
        experience_max=_as_int(experience.get("max")),
        education=str(education.get("name") or education or ""),
        salary_text=str(salary.get("name") or salary or ""),
        posted_at=str(item.get("posting-date") or item.get("posting_timestamp") or ""),
        deadline_at=str(item.get("expiration-date") or item.get("expiration_timestamp") or ""),
        description=description,
        skills_raw=extract_skills(description),
        collected_at=collected_at,
        industry=str(industry.get("name") or ""),
        company_type="",
    )


def _is_target_role(job: JobPosting) -> bool:
    text = f"{job.title} {job.description} {' '.join(job.skills_raw)}".lower()
    if any(keyword in text for keyword in TARGET_ROLE_KEYWORDS):
        return True
    strong_skills = {"ML", "MLOps", "LLM", "RAG", "PyTorch", "TensorFlow", "scikit-learn"}
    return bool(strong_skills.intersection(set(job.skills_raw)))


def _looks_like_standard_fixture(item: dict[str, Any]) -> bool:
    return "external_id" in item and "company" in item and "title" in item


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
