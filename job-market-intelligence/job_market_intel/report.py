from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .analyze import analyze_jobs
from .models import JobPosting


def write_report(
    reports_dir: Path,
    jobs: list[JobPosting],
    scored_records: list[dict[str, Any]],
    counts: dict[str, int],
) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    analysis = analyze_jobs(jobs)
    markdown = render_markdown_report(analysis, scored_records, counts)
    md_path = reports_dir / "job_market_report.md"
    html_path = reports_dir / "job_market_report.html"
    md_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(render_html(markdown), encoding="utf-8")
    write_artifact_contract(reports_dir, scored_records, counts)
    return md_path, html_path


def write_artifact_contract(
    reports_dir: Path,
    scored_records: list[dict[str, Any]],
    counts: dict[str, int],
) -> dict[str, Path]:
    normalized_jobs = int(counts.get("normalized_jobs", 0))
    scored_jobs = int(counts.get("scored_jobs", 0))
    raw_items = int(counts.get("raw_latest_items", 0))
    score_explanations_complete = bool(scored_records) and all(
        row.get("score_breakdown") and row.get("resume_bullets") for row in scored_records
    )
    checks = [
        {"check": "raw_input_present", "passed": raw_items > 0, "detail": f"raw_latest_items={raw_items}"},
        {
            "check": "normalized_jobs_present",
            "passed": normalized_jobs > 0,
            "detail": f"normalized_jobs={normalized_jobs}",
        },
        {
            "check": "all_normalized_jobs_scored",
            "passed": scored_jobs == normalized_jobs and scored_jobs > 0,
            "detail": f"scored_jobs={scored_jobs}, normalized_jobs={normalized_jobs}",
        },
        {
            "check": "score_explanations_complete",
            "passed": score_explanations_complete,
            "detail": "every scored job has breakdown and evidence-based resume bullets",
        },
    ]
    quality_path = reports_dir / "quality_gate_checks.csv"
    with quality_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check", "passed", "detail"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(checks)

    generated_at = datetime.now(timezone.utc).isoformat()
    final_report = reports_dir / "final_report.md"
    final_report.write_text(
        "\n".join(
            [
                "# Job Market Intelligence Final Report",
                "",
                "## 결론",
                "",
                f"공식 API boundary와 fixture fallback 아래 raw {raw_items}건을 정규화·중복 제거해 {normalized_jobs}건을 만들고, {scored_jobs}건 모두에 설명 가능한 지원 우선순위를 부여했다.",
                "",
                "## 운영 판단",
                "",
                "현재 fixture 결과는 pipeline 재현 근거이며 실제 채용시장 통계가 아니다. 실제 지원 판단에는 공식 API로 다시 수집한 결과와 개인 application outcome을 함께 사용해야 한다.",
                "",
                "## Artifact contract",
                "",
                "- `job_market_report.md`와 `job_market_report.html`: 평가자용 결과",
                "- `run_summary.json`: machine-readable 실행 요약",
                "- `quality_gate_checks.csv`: 관측 가능한 pipeline gate",
                "- `model_card.md`: rule-based ranking의 사용 범위와 한계",
                "- `data_source_and_contract.md`: source·privacy·출력 경계",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    model_card = reports_dir / "model_card.md"
    model_card.write_text(
        "# Job Fit Ranking System Card\n\n"
        "Rule-based fit score는 role, skill, domain, experience, location, profile evidence와 risk penalty를 결합한다. "
        "지원 순서를 설명 가능하게 정렬하는 decision-support 도구이며 채용 가능성 예측이나 자동 지원 권한이 아니다.\n",
        encoding="utf-8",
    )
    data_contract = reports_dir / "data_source_and_contract.md"
    data_contract.write_text(
        "# Data Source and Contract\n\n"
        "- 입력은 공식 provider API 또는 repository fixture로 제한한다.\n"
        "- 무단 scraping, 개인 식별정보 수집, credential 출력은 허용하지 않는다.\n"
        "- raw response는 원형을 보존하고 normalized/scored table은 재생성 가능하게 유지한다.\n"
        "- fixture 결과는 재현성 검증용이며 시장 통계로 해석하지 않는다.\n",
        encoding="utf-8",
    )
    run_summary = reports_dir / "run_summary.json"
    run_summary.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generated_at_utc": generated_at,
                "status": "pass" if all(row["passed"] for row in checks) else "fail",
                "counts": {
                    "raw_latest_items": raw_items,
                    "normalized_jobs": normalized_jobs,
                    "scored_jobs": scored_jobs,
                },
                "quality_gate_passed": all(row["passed"] for row in checks),
                "reports": {
                    "markdown": "reports/job_market_report.md",
                    "html": "reports/job_market_report.html",
                    "final_report": "reports/final_report.md",
                    "model_card": "reports/model_card.md",
                    "data_source_and_contract": "reports/data_source_and_contract.md",
                    "quality_gate": "reports/quality_gate_checks.csv",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "final_report": final_report,
        "model_card": model_card,
        "data_source_and_contract": data_contract,
        "run_summary": run_summary,
        "quality_gate": quality_path,
    }


def render_markdown_report(
    analysis: dict[str, Any],
    scored_records: list[dict[str, Any]],
    counts: dict[str, int],
) -> str:
    top = scored_records[:10]
    skill_counts = analysis.get("skill_counts", {})
    skill_gap_counts = _skill_gap_counts(scored_records)
    lines = [
        "# Job Market Intelligence Report",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 오늘의 시장 요약",
        "",
        f"- Raw latest items: {counts.get('raw_latest_items', 0)}",
        f"- Normalized target jobs: {counts.get('normalized_jobs', 0)}",
        f"- Scored jobs: {counts.get('scored_jobs', 0)}",
        f"- Deadline soon jobs: {analysis.get('deadline_soon_count', 0)}",
        f"- Recent postings: {analysis.get('recent_posting_count', 0)}",
        "",
        "## 상위 추천 공고",
        "",
        "| 순위 | 회사 | 공고 | 점수 | 우선순위 | Skill gap |",
        "|---:|---|---|---:|---|---|",
    ]
    for rank, record in enumerate(top, start=1):
        gap = ", ".join(record.get("skill_gap", [])[:4]) or "-"
        lines.append(
            f"| {rank} | {record['company']} | [{record['title']}]({record['url']}) | "
            f"{record['fit_score']:.2f} | {record['priority']} | {gap} |"
        )
    lines.extend(["", "## 점수 근거와 Resume Bullet 초안", ""])
    for record in top[:5]:
        lines.extend(
            [
                f"### {record['company']} - {record['title']}",
                "",
                f"- Fit score: {record['fit_score']:.2f}",
                f"- Priority: {record['priority']}",
                f"- Score breakdown: `{json.dumps(record['score_breakdown'], ensure_ascii=False)}`",
                f"- Skill gap: {', '.join(record.get('skill_gap', [])) or '-'}",
                "- Resume bullets:",
            ]
        )
        for bullet in record.get("resume_bullets", []):
            lines.append(f"  - {bullet}")
        lines.append("")
    lines.extend(
        [
            "## 가장 많이 요구되는 기술",
            "",
            _counter_table(skill_counts, "Skill"),
            "",
            "## 내 Skill Gap",
            "",
            _counter_table(skill_gap_counts, "Skill gap"),
            "",
            "## 지원 액션 리스트",
            "",
        ]
    )
    for record in top:
        action = "지원서 맞춤 작성" if record["priority"] == "apply_now" else "모니터링"
        lines.append(f"- `{record['priority']}` {record['company']} / {record['title']}: {action}")
    lines.extend(
        [
            "",
            "## 포트폴리오 인사이트",
            "",
            "- 단순 공고 모음이 아니라 role, skill, domain, evidence를 연결한 decision system으로 설명한다.",
            "- 상위 공고의 score breakdown과 skill gap을 이력서 업데이트 backlog로 사용한다.",
            "- 공식 API와 fixture fallback을 분리해 재현성과 compliance를 동시에 확보한다.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(markdown: str) -> str:
    body = html.escape(markdown)
    return (
        "<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
        "<title>Job Market Intelligence Report</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:980px;margin:32px auto;"
        "line-height:1.55;color:#1f2937}pre{white-space:pre-wrap;background:#f8fafc;"
        "padding:20px;border:1px solid #e5e7eb}</style></head><body>"
        f"<pre>{body}</pre></body></html>"
    )


def _counter_table(counter: dict[str, int], label: str) -> str:
    if not counter:
        return "_No data_"
    rows = [f"| {label} | Count |", "|---|---:|"]
    for key, count in list(counter.items())[:15]:
        rows.append(f"| {key} | {count} |")
    return "\n".join(rows)


def _skill_gap_counts(scored_records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in scored_records:
        for skill in record.get("skill_gap", []):
            counts[skill] = counts.get(skill, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0].lower())))
