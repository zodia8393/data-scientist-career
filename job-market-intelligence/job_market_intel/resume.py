from __future__ import annotations

from typing import Any

from .models import JobPosting


def matched_projects(job: JobPosting, profile: dict[str, Any]) -> list[dict[str, Any]]:
    job_skills = {skill.lower() for skill in job.skills_raw}
    text = f"{job.title} {job.description} {job.industry}".lower()
    matches: list[dict[str, Any]] = []
    for project in profile.get("projects", []):
        project_skills = {str(skill).lower() for skill in project.get("skills", [])}
        project_domains = {str(domain).lower() for domain in project.get("domains", [])}
        skill_overlap = sorted(job_skills.intersection(project_skills))
        domain_overlap = sorted(domain for domain in project_domains if domain in text)
        if skill_overlap or domain_overlap:
            matches.append(
                {
                    "name": project.get("name", ""),
                    "skill_overlap": skill_overlap,
                    "domain_overlap": domain_overlap,
                    "evidence_bullets": list(project.get("evidence_bullets", []))[:3],
                }
            )
    return matches


def generate_resume_bullets(job: JobPosting, project_matches: list[dict[str, Any]]) -> list[str]:
    bullets: list[str] = []
    for project in project_matches:
        project_name = project.get("name", "프로젝트")
        skills = ", ".join(project.get("skill_overlap", [])[:4])
        suffix = f" 관련 역량({skills})" if skills else " 관련 도메인 경험"
        for evidence in project.get("evidence_bullets", [])[:2]:
            bullets.append(f"{project_name}: {evidence} 이 근거로 {job.title}의{suffix}을 설명할 수 있다.")
            if len(bullets) >= 5:
                return bullets
    if len(bullets) < 3:
        bullets.append("등록된 profile evidence만으로는 추가 bullet 생성 근거가 부족하므로, 해당 공고 지원 전 프로젝트 근거를 보강한다.")
    return bullets[:5]
