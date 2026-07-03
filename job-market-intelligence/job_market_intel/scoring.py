from __future__ import annotations

from typing import Any

from .models import JobPosting, ScoreResult
from .resume import generate_resume_bullets, matched_projects
from .skills import canonical_skill_set


def score_jobs(jobs: list[JobPosting], profile: dict[str, Any]) -> list[ScoreResult]:
    return sorted((score_job(job, profile) for job in jobs), key=lambda result: result.fit_score, reverse=True)


def score_job(job: JobPosting, profile: dict[str, Any]) -> ScoreResult:
    text = f"{job.title} {job.description} {job.industry} {job.company_type}".lower()
    job_skills = canonical_skill_set(job.skills_raw)
    profile_skills = canonical_skill_set(profile.get("skills", []))
    skill_overlap = job_skills.intersection(profile_skills)
    skill_gap = sorted(job_skills - profile_skills, key=str.lower)
    projects = matched_projects(job, profile)

    role_match = _role_match(text, profile.get("target_roles", []))
    skill_match = _ratio_score(len(skill_overlap), len(job_skills), max_points=25.0)
    domain_match = _domain_match(text, profile.get("domains", []))
    experience_fit = _experience_fit(job, profile.get("experience_years"))
    location_fit = _location_fit(job.location.lower(), profile.get("preferred_locations", []))
    portfolio_evidence = min(15.0, 5.0 * len(projects) + 2.0 * sum(len(p["evidence_bullets"]) for p in projects))
    risk_penalty = _risk_penalty(text, profile.get("avoid_keywords", []))

    raw_score = role_match + skill_match + domain_match + experience_fit + location_fit + portfolio_evidence
    fit_score = max(0.0, min(100.0, raw_score - risk_penalty))
    breakdown = {
        "role_match": round(role_match, 2),
        "skill_match": round(skill_match, 2),
        "domain_match": round(domain_match, 2),
        "experience_fit": round(experience_fit, 2),
        "location_fit": round(location_fit, 2),
        "portfolio_evidence": round(portfolio_evidence, 2),
        "risk_penalty": round(risk_penalty, 2),
    }
    return ScoreResult(
        job=job,
        fit_score=round(fit_score, 2),
        priority=_priority(fit_score),
        score_breakdown=breakdown,
        skill_gap=skill_gap,
        matched_projects=projects,
        resume_bullets=generate_resume_bullets(job, projects),
    )


def _role_match(text: str, target_roles: list[str]) -> float:
    if any(role and role in text for role in target_roles):
        return 20.0
    role_tokens = ("data", "scientist", "ml", "ai", "machine learning", "분석")
    hits = sum(1 for token in role_tokens if token in text)
    return min(15.0, hits * 3.0)


def _domain_match(text: str, domains: list[str]) -> float:
    if not domains:
        return 0.0
    hits = sum(1 for domain in domains if domain and domain in text)
    return _ratio_score(hits, len(domains), max_points=15.0)


def _experience_fit(job: JobPosting, years: Any) -> float:
    if years is None:
        return 8.0
    try:
        user_years = float(years)
    except (TypeError, ValueError):
        return 8.0
    min_years = job.experience_min
    max_years = job.experience_max
    if min_years is None and max_years is None:
        return 10.0
    if min_years is not None and user_years < min_years:
        return max(0.0, 10.0 - (min_years - user_years) * 3.0)
    if max_years is not None and max_years > 0 and user_years > max_years + 3:
        return 7.0
    return 10.0


def _location_fit(location: str, preferred: list[str]) -> float:
    if not preferred:
        return 5.0
    return 10.0 if any(place and place in location for place in preferred) else 2.0


def _risk_penalty(text: str, avoid_keywords: list[str]) -> float:
    return min(20.0, 8.0 * sum(1 for keyword in avoid_keywords if keyword and keyword in text))


def _ratio_score(numerator: int, denominator: int, max_points: float) -> float:
    if denominator <= 0:
        return 0.0
    return min(max_points, max_points * numerator / denominator)


def _priority(score: float) -> str:
    if score >= 75:
        return "apply_now"
    if score >= 60:
        return "watch"
    return "skip"
