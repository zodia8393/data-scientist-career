#!/usr/bin/env python3
"""Validate research/product-grade weekend portfolio project contracts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_REGISTRY = Path("/workspace/prj/data-scientist-career/registry/projects.json")
DEFAULT_ARTIFACT_ROOT = Path("/DATA/HJ/prj/data-scientist-career/projects")
DEFAULT_STATE_FILE = Path("/DATA/HJ/prj/data-scientist-career/state/weekend-project-state.md")
BASE_QUALITY_FLOOR = 92.0
BASE_README_PRESENTATION_FLOOR = 94.0
README_MAX_LINES = 240
README_AVG_PARAGRAPH_MAX = 180
README_LONG_PARAGRAPH_WARN = 520
README_MAX_TABLE_WIDTH = 4

CORE_REQUIRED_FILES = [
    "README.md",
    "docs/data_contract.md",
    "docs/modeling_protocol.md",
    "docs/reproducibility.md",
    "scripts/run_all.sh",
    "pyproject.toml",
    "requirements.txt",
    "tests/test_pipeline.py",
]

RESEARCH_PRODUCT_FILES = [
    ".github/workflows/ci.yml",
    "docs/topic_selection.md",
    "docs/research_design.md",
    "docs/system_design.md",
    "docs/privacy_publication_gate.md",
    "docs/hiring_market_alignment.md",
    "docs/research_gap_report.md",
]

DOC_MARKERS: dict[str, tuple[tuple[str, ...], ...]] = {
    "README.md": (
        ("결론",),
        ("무엇을 만들었나", "what was built"),
        ("핵심 수치", "key metrics"),
        ("의미", "so what"),
        ("얻은 인사이트", "insight"),
        ("방법 선택 이유", "method rationale", "why this method"),
        ("의사결정", "decision"),
        ("실행", "run", "usage"),
    ),
    "docs/topic_selection.md": (("후보", "candidate"), ("채용", "hiring", "market")),
    "docs/data_contract.md": (("라이선스", "license"), ("join", "결합"), ("누수", "leakage")),
    "docs/modeling_protocol.md": (("baseline", "기준선"), ("split", "분할"), ("metric", "지표")),
    "docs/research_design.md": (("연구 질문", "research question"), ("ablation", "절제"), ("불확실", "uncertainty")),
    "docs/system_design.md": (("API", "CLI", "dashboard", "batch", "product surface"), ("배포", "deployment", "runbook")),
    "docs/privacy_publication_gate.md": (("개인정보", "PII"), ("내부", "internal"), ("SNS", "social")),
    "docs/hiring_market_alignment.md": (("채용", "hiring"), ("역량", "signal", "competency")),
    "docs/reproducibility.md": (("pytest", "test"), ("run_all", "재현")),
    "docs/research_gap_report.md": (("gap", "미달", "다음"),),
}

SECRET_VALUE_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+]{16,}"
)
LOCAL_ABSOLUTE_PATH_RE = re.compile(r"(?<![\w.-])/(?:workspace|DATA/HJ|home/ybs)\b")
ACTIVE_FLOOR_RE = re.compile(r"Active quality score floor:\s*`(?P<score>\d+(?:\.\d+)?)`")
TEXT_EXTENSIONS = {".md", ".py", ".sh", ".toml", ".txt", ".yml", ".yaml", ".json", ".csv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Project source directory")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--stage", choices=["saturday", "sunday"], default="sunday")
    parser.add_argument(
        "--ratchet-mode",
        choices=["strict", "floor"],
        default="strict",
        help="strict requires quality to exceed the active floor; floor only checks current floor compliance",
    )
    parser.add_argument("--run-smoke", action="store_true", help="Run scripts/run_all.sh after static checks")
    return parser.parse_args()


def has_hangul(text: str, minimum: int = 20) -> bool:
    return sum(1 for char in text if "\uac00" <= char <= "\ud7a3") >= minimum


def record_check(checks: list[str], name: str, status: str, detail: str) -> None:
    if status not in {"PASS", "WARN", "FAIL"}:
        raise ValueError(f"invalid check status: {status}")
    checks.append(status)
    print(f"{status} {name}: {detail}")


def run_check(checks: list[str], name: str, passed: bool, detail: str) -> None:
    record_check(checks, name, "PASS" if passed else "FAIL", detail)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def contains_marker_group(text: str, marker_group: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(marker.lower() in lower for marker in marker_group)


def first_line_number(lines: list[str], needle: str) -> int | None:
    lower_needle = needle.lower()
    for idx, line in enumerate(lines, start=1):
        if lower_needle in line.lower():
            return idx
    return None


def markdown_table_widths(lines: list[str]) -> list[int]:
    widths: list[int] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        widths.append(len(stripped.split("|")[1:-1]))
    return widths


def prose_paragraph_lengths(text: str) -> list[int]:
    lengths: list[int] = []
    in_code = False
    for paragraph in text.split("\n\n"):
        lines: list[str] = []
        for line in paragraph.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if not stripped:
                continue
            if stripped.startswith(("#", "|", "-", "*", ">", "```")):
                continue
            lines.append(stripped)
        if lines:
            lengths.append(len(" ".join(lines)))
    return lengths


def unresolved_todos(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if re.search(r"\b(TODO|TBD|FIXME)\b", line, re.IGNORECASE)
    ]


def load_registry_project(registry: Path, slug: str) -> dict | None:
    if not registry.is_file():
        return None
    try:
        data = json.loads(read_text(registry))
    except json.JSONDecodeError:
        return None
    for item in data.get("projects", []):
        if item.get("slug") == slug:
            return item
    return None


def resolve_artifact_path(project: Path, registry: Path, artifact_root: Path) -> Path:
    item = load_registry_project(registry, project.name)
    if item and item.get("artifact_path"):
        return Path(str(item["artifact_path"]))
    return artifact_root / project.name


def load_active_quality_floor(state_file: Path) -> float:
    if not state_file.is_file():
        return BASE_QUALITY_FLOOR
    match = ACTIVE_FLOOR_RE.search(read_text(state_file))
    if not match:
        return BASE_QUALITY_FLOOR
    return max(BASE_QUALITY_FLOOR, float(match.group("score")))


def parse_score(raw_score: str) -> tuple[float | None, str | None]:
    raw = raw_score.strip()
    try:
        score = float(raw)
    except ValueError:
        return None, "non-numeric score"
    if score < 0 or score >= 100:
        return None, "score must satisfy 0 <= score < 100; 100 is not allowed"
    if score >= 99 and "." not in raw:
        return None, "scores >=99 must be written with decimal precision"
    return score, None


def validate_docs(project: Path, stage: str, checks: list[str]) -> None:
    for relative_path, marker_groups in DOC_MARKERS.items():
        path = project / relative_path
        if not path.is_file():
            continue
        text = read_text(path)
        run_check(checks, f"korean_doc:{relative_path}", has_hangul(text), "contains Korean explanatory text")
        for marker_group in marker_groups:
            run_check(
                checks,
                f"doc_marker:{relative_path}:{'/'.join(marker_group)}",
                contains_marker_group(text, marker_group),
                "required research/product marker present",
            )
        if stage == "sunday" and relative_path != "docs/research_gap_report.md":
            todos = unresolved_todos(text)
            run_check(
                checks,
                f"no_unresolved_todo:{relative_path}",
                not todos,
                "no TODO/TBD/FIXME" if not todos else "; ".join(todos[:3]),
            )


def validate_readme_floor(project: Path, stage: str, checks: list[str]) -> None:
    path = project / "README.md"
    if not path.is_file():
        return
    text = read_text(path)
    lines = text.splitlines()
    conclusion_line = first_line_number(lines, "## 결론")
    metrics_line = first_line_number(lines, "## 핵심 수치")
    insights_line = first_line_number(lines, "## 얻은 인사이트")
    method_line = first_line_number(lines, "## 방법 선택 이유")

    run_check(
        checks,
        "readme_floor:conclusion_first",
        conclusion_line is not None and conclusion_line <= 20,
        f"## 결론 line={conclusion_line}" if conclusion_line else "missing ## 결론",
    )
    run_check(
        checks,
        "readme_floor:core_sections_order",
        all(line is not None for line in [conclusion_line, metrics_line, insights_line, method_line])
        and conclusion_line < metrics_line < insights_line < method_line,
        "결론 -> 핵심 수치 -> 얻은 인사이트 -> 방법 선택 이유",
    )
    run_check(
        checks,
        "readme_floor:metric_meaning_column",
        "## 핵심 수치" in text and "| 항목 | 값 | 의미 |" in text,
        "핵심 수치 table includes an explicit 의미 column",
    )
    run_check(
        checks,
        "readme_floor:no_interview_prompt_section",
        "면접에서 설명할 포인트" not in text,
        "avoid portfolio README filler aimed at the interviewer",
    )
    table_widths = markdown_table_widths(lines)
    max_table_width = max(table_widths) if table_widths else 0
    paragraph_lengths = prose_paragraph_lengths(text)
    avg_paragraph = (
        sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    )
    longest_paragraph = max(paragraph_lengths) if paragraph_lengths else 0
    run_check(
        checks,
        "readme_ui:max_table_width",
        max_table_width <= README_MAX_TABLE_WIDTH,
        f"max table width {max_table_width} <= {README_MAX_TABLE_WIDTH}",
    )
    run_check(
        checks,
        "readme_ui:avg_paragraph_length",
        avg_paragraph <= README_AVG_PARAGRAPH_MAX,
        f"avg paragraph length {avg_paragraph:.1f} <= {README_AVG_PARAGRAPH_MAX}",
    )
    run_check(
        checks,
        "readme_ui:longest_paragraph",
        longest_paragraph <= README_LONG_PARAGRAPH_WARN,
        f"longest paragraph {longest_paragraph} <= {README_LONG_PARAGRAPH_WARN}",
    )
    run_check(
        checks,
        "readme_ui:scan_sections",
        all(
            marker in text
            for marker in ["## 결론", "## 핵심 수치", "## 얻은 인사이트", "## 방법 선택 이유", "## 대표 시각화"]
        ),
        "conclusion, metrics, insights, method rationale, visual sections present",
    )
    if stage == "sunday":
        run_check(
            checks,
            "readme_floor:concise",
            len(lines) <= README_MAX_LINES,
            f"{len(lines)} lines <= {README_MAX_LINES}",
        )
        run_check(
            checks,
            "readme_floor:public_paths",
            LOCAL_ABSOLUTE_PATH_RE.search(text) is None,
            "no /workspace, /DATA/HJ, or /home/ybs absolute paths in GitHub README",
        )


def validate_run_script(project: Path, checks: list[str]) -> None:
    run_script = project / "scripts/run_all.sh"
    if not run_script.is_file():
        return
    result = subprocess.run(["bash", "-n", str(run_script)], text=True, capture_output=True, check=False)
    run_check(checks, "bash_n:run_all", result.returncode == 0, result.stderr.strip() or "syntax ok")


def validate_python(project: Path, checks: list[str]) -> None:
    src_files = sorted((project / "src").glob("**/*.py")) if (project / "src").is_dir() else []
    test_files = sorted((project / "tests").glob("**/*.py")) if (project / "tests").is_dir() else []
    py_files = src_files + test_files
    if not py_files:
        run_check(checks, "py_compile", False, "no Python files under src/ or tests/")
        return
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, py_files)],
        text=True,
        capture_output=True,
        check=False,
    )
    run_check(checks, "py_compile", result.returncode == 0, result.stderr.strip() or f"{len(py_files)} files")


def validate_registry(registry: Path, checks: list[str]) -> None:
    if not registry.is_file():
        run_check(checks, "registry_json", False, str(registry))
        return
    try:
        data = json.loads(read_text(registry))
    except json.JSONDecodeError as exc:
        run_check(checks, "registry_json", False, str(exc))
        return
    run_check(checks, "registry_json", isinstance(data.get("projects"), list), str(registry))


def parse_quality_gate(path: Path, active_floor: float, ratchet_mode: str) -> tuple[bool, str]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        return False, f"read failed: {exc}"
    if not rows:
        return False, f"empty file: {path}"
    if "score" in rows[0]:
        scores: list[float] = []
        presentation_scores: list[float] = []
        for row in rows:
            score, error = parse_score(str(row.get("score", "")))
            if error:
                category = str(row.get("category", "")).strip() or "unknown category"
                return False, f"{error} in {path}: {category}"
            scores.append(score)
            category = str(row.get("category", "")).lower()
            if "portfolio presentation" in category or "readme" in category:
                presentation_scores.append(score)
        min_score = min(scores)
        min_presentation = min(presentation_scores) if presentation_scores else None
        presentation_floor = max(BASE_README_PRESENTATION_FLOOR, active_floor)
        if ratchet_mode == "strict":
            passed = min_score > active_floor
            score_rule = f"min_score={min_score:g}>{active_floor:g}"
        else:
            passed = min_score >= active_floor
            score_rule = f"min_score={min_score:g}>={active_floor:g}"
        if min_presentation is not None:
            passed = passed and min_presentation >= presentation_floor
        ratchet_note = "ratchet_ok" if min_score > active_floor else "ratchet_required"
        detail = (
            f"{path}, {score_rule}, {ratchet_note}, "
            f"presentation_min={min_presentation if min_presentation is not None else 'n/a'}"
            f">={presentation_floor:g}, categories={len(scores)}, scores_are_lt_100"
        )
        return passed, detail
    if "passed" in rows[0]:
        failed = [row for row in rows if str(row.get("passed", "")).lower() not in {"true", "1", "yes"}]
        return not failed, f"{path}, checks={len(rows)}, failed={len(failed)}"
    return False, f"unrecognized schema: {path}"


def parse_prepublish_audit(reports_dir: Path) -> tuple[bool, str] | None:
    json_path = reports_dir / "prepublish_audit.json"
    if json_path.is_file():
        try:
            payload = json.loads(read_text(json_path))
        except json.JSONDecodeError as exc:
            return False, f"{json_path}, invalid json: {exc}"
        allowed = bool(payload.get("public_registry_allowed", payload.get("passed", False)))
        status = payload.get("status", "unknown")
        failed = [
            str(item.get("check", "unknown"))
            for item in payload.get("checks", [])
            if not bool(item.get("passed", False))
        ]
        detail = f"{json_path}, status={status}, public_registry_allowed={allowed}"
        if failed:
            detail += f", failed={','.join(failed)}"
        return allowed, detail

    csv_path = reports_dir / "prepublish_audit.csv"
    if csv_path.is_file():
        try:
            with csv_path.open(newline="", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
        except OSError as exc:
            return False, f"{csv_path}, read failed: {exc}"
        if not rows or "passed" not in rows[0]:
            return False, f"{csv_path}, unrecognized schema"
        failed = [
            str(row.get("check", "unknown"))
            for row in rows
            if str(row.get("passed", "")).lower() not in {"true", "1", "yes"}
        ]
        return not failed, f"{csv_path}, checks={len(rows)}, failed={len(failed)}"

    return None


def validate_artifacts(
    artifact_path: Path,
    stage: str,
    checks: list[str],
    active_floor: float,
    ratchet_mode: str,
) -> None:
    reports_dir = artifact_path / "reports"
    if stage == "saturday":
        record_check(
            checks,
            "artifact_root",
            "PASS" if artifact_path.exists() else "WARN",
            str(artifact_path) if artifact_path.exists() else "artifact root may be created by first run",
        )
        return

    run_check(checks, "artifact_root", artifact_path.is_dir(), str(artifact_path))
    for relative_path in [
        "reports/final_report.md",
        "reports/model_card.md",
        "reports/data_source_and_contract.md",
        "reports/run_summary.json",
    ]:
        path = artifact_path / relative_path
        run_check(checks, f"artifact_file:{relative_path}", path.is_file(), str(path))

    candidates = [
        reports_dir / "quality_gate_scores.csv",
        reports_dir / "quality_gate_checks.csv",
    ]
    existing = [path for path in candidates if path.is_file()]
    if not existing:
        run_check(checks, "quality_gate_artifact", False, f"missing one of: {', '.join(map(str, candidates))}")
        return
    passed, detail = parse_quality_gate(existing[0], active_floor, ratchet_mode)
    run_check(checks, "quality_gate_artifact", passed, detail)

    prepublish_result = parse_prepublish_audit(reports_dir)
    if prepublish_result is not None:
        prepublish_passed, prepublish_detail = prepublish_result
        run_check(checks, "prepublish_audit", prepublish_passed, prepublish_detail)


def validate_product_surface(project: Path, checks: list[str]) -> None:
    surface_files = [
        project / "scripts/run_all.sh",
        project / "src",
        project / "app.py",
        project / "api.py",
        project / "dashboard.py",
        project / "Dockerfile",
    ]
    run_check(
        checks,
        "product_surface",
        any(path.exists() for path in surface_files),
        "has batch/API/app/dashboard/deploy surface",
    )


def validate_privacy_scan(project: Path, checks: list[str]) -> None:
    findings: list[str] = []
    for path in project.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if SECRET_VALUE_RE.search(read_text(path)):
            findings.append(str(path.relative_to(project)))
    run_check(
        checks,
        "secret_value_scan",
        not findings,
        "no obvious token/secret assignments" if not findings else ", ".join(findings[:5]),
    )


def run_smoke(project: Path, checks: list[str]) -> None:
    result = subprocess.run(
        ["bash", "scripts/run_all.sh"],
        cwd=project,
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )
    detail = (result.stdout + result.stderr).strip().splitlines()
    run_check(
        checks,
        "smoke:run_all",
        result.returncode == 0,
        detail[-1] if detail else f"exit={result.returncode}",
    )


def main() -> int:
    args = parse_args()
    project = Path(args.project)
    registry = Path(args.registry)
    artifact_root = Path(args.artifact_root)
    active_floor = load_active_quality_floor(Path(args.state_file))
    artifact_path = resolve_artifact_path(project, registry, artifact_root)
    checks: list[str] = []

    run_check(checks, "project_dir", project.is_dir(), str(project))

    required_files = CORE_REQUIRED_FILES + RESEARCH_PRODUCT_FILES
    for relative_path in required_files:
        path = project / relative_path
        run_check(checks, f"required_file:{relative_path}", path.is_file(), str(path))

    validate_docs(project, args.stage, checks)
    validate_readme_floor(project, args.stage, checks)
    validate_run_script(project, checks)
    validate_python(project, checks)
    validate_registry(registry, checks)
    validate_product_surface(project, checks)
    validate_privacy_scan(project, checks)
    validate_artifacts(artifact_path, args.stage, checks, active_floor, args.ratchet_mode)
    if args.run_smoke:
        run_smoke(project, checks)

    return 0 if "FAIL" not in checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
