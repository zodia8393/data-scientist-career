from __future__ import annotations

import html
import json
from datetime import datetime
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
    return md_path, html_path


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
