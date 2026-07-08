#!/usr/bin/env python3
"""Update a project's research gap report from quality-ratchet scores."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY = Path("/workspace/prj/personal/data-scientist-career/registry/projects.json")
DEFAULT_SOURCE_ROOT = Path("/workspace/prj/personal/data-scientist-career")
DEFAULT_STATE_FILE = Path("/DATA/HJ/prj/data-scientist-career/state/weekend-project-state.md")
BASE_QUALITY_FLOOR = 92.0
BASE_README_PRESENTATION_FLOOR = 94.0

ACTIVE_FLOOR_RE = re.compile(r"Active quality score floor:\s*`(?P<score>\d+(?:\.\d+)?)`")
START_MARKER = "<!-- AUTO_QUALITY_RATCHET_GAP_START -->"
END_MARKER = "<!-- AUTO_QUALITY_RATCHET_GAP_END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality-gate", required=True, help="quality_gate_scores.csv path")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--project", help="Project source directory; inferred when omitted")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_active_floor(state_file: Path) -> float:
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


def load_quality_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"empty quality gate file: {path}")
    if "score" not in rows[0]:
        raise ValueError(f"quality gate file has no score column: {path}")

    parsed: list[dict[str, Any]] = []
    for row in rows:
        category = str(row.get("category", "")).strip() or "unknown category"
        score, error = parse_score(str(row.get("score", "")))
        if error:
            raise ValueError(f"{error} in {path}: {category}")
        parsed.append(
            {
                "category": category,
                "score": score,
                "evidence": str(row.get("evidence", "")).strip(),
            }
        )
    return parsed


def infer_project_path(
    *,
    quality_gate: Path,
    registry: Path,
    source_root: Path,
    explicit_project: str | None,
) -> Path:
    if explicit_project:
        return Path(explicit_project)

    if registry.is_file():
        try:
            data = json.loads(read_text(registry))
        except json.JSONDecodeError:
            data = {}
        for item in data.get("projects", []):
            artifact_path = item.get("artifact_path")
            source_path = item.get("source_path")
            if artifact_path and source_path:
                try:
                    quality_gate.resolve().relative_to(Path(str(artifact_path)).resolve())
                except ValueError:
                    continue
                return Path(str(source_path))

    parts = quality_gate.parts
    if "projects" in parts:
        idx = parts.index("projects")
        if idx + 1 < len(parts):
            return source_root / parts[idx + 1]
    raise ValueError(f"cannot infer project path from {quality_gate}")


def recommendation_for(category: str) -> str:
    lower = category.lower()
    if "problem framing" in lower:
        return "채용시장/운영 의사결정 문장을 더 선명하게 만들고, README 결론에 비용·리스크·사용자 행동 변화를 연결한다."
    if "data quality" in lower:
        return "데이터 source를 하나 더 검증하거나 join coverage, license, leakage risk를 수치로 보강한다."
    if "eda" in lower:
        return "segment별 패턴, 실패 구간, outlier/drift 원인을 figure와 함께 추가한다."
    if "feature engineering" in lower or "statistical design" in lower:
        return "ablation 가능한 feature family를 추가하고, 제거 실험으로 실제 기여를 검증한다."
    if "modeling" in lower or "method rigor" in lower:
        return "baseline 외 강한 benchmark나 ablation을 추가하고, 성능 차이를 confidence interval과 함께 제시한다."
    if "validation" in lower or "reproducibility" in lower:
        return "temporal/group/prospective validation을 강화하고 validator/CI에 재현 명령을 포함한다."
    if "interpretation" in lower or "decision usefulness" in lower:
        return "모델 결과를 reviewer가 실행 가능한 운영 의사결정, threshold, action list로 변환한다."
    if "code quality" in lower or "automation" in lower:
        return "one-shot run, typed modules, smoke tests, deployment/readiness check를 추가해 반복 실행성을 높인다."
    if "portfolio presentation" in lower or "readme" in lower:
        return "README 첫 화면을 더 짧게 만들고, 핵심 수치의 의미·인사이트·방법 선택 이유를 더 직접적으로 쓴다."
    if "doctoral" in lower or "originality" in lower:
        return "단순 모델 성능을 넘어 prospective validation, causal/robustness angle, productized decision loop를 보강한다. evaluator가 이미 있다면 충분한 snapshot coverage 후 true outcome calibration을 추가한다."
    return "현재 evidence를 기준으로 reviewer가 납득할 추가 실험, 문서, 검증 명령을 하나 이상 보강한다."


def build_gap_section(
    *,
    quality_gate: Path,
    active_floor: float,
    project: Path,
    rows: list[dict[str, Any]],
) -> tuple[str, int]:
    presentation_floor = max(BASE_README_PRESENTATION_FLOOR, active_floor)
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M KST")
    gap_rows: list[list[str]] = []

    for row in sorted(rows, key=lambda item: float(item["score"])):
        category = str(row["category"])
        score = float(row["score"])
        required = presentation_floor if ("portfolio presentation" in category.lower() or "readme" in category.lower()) else active_floor
        if score > active_floor and score >= required:
            continue
        if score == active_floor:
            reason = "active floor와 동점이라 ratchet 상승을 만들지 못함"
        elif score < required:
            reason = f"required {required:g} 미만"
        else:
            reason = "ratchet 조건 미충족"
        gap_rows.append(
            [
                category,
                f"{score:g}",
                f">{active_floor:g}" if required == active_floor else f">={required:g}",
                reason,
                recommendation_for(category),
            ]
        )

    if not gap_rows:
        status = "현재 quality score는 run-start floor를 초과합니다. postcheck가 state floor ratchet을 수행할 수 있습니다."
    else:
        status = "현재 quality score는 아직 ratchet 완료 상태가 아닙니다. 아래 항목을 보강한 뒤 재측정해야 합니다."

    lines = [
        START_MARKER,
        "## Quality Ratchet Gap",
        "",
        f"- Generated: `{generated_at}`",
        f"- Quality artifact: `{quality_gate}`",
        f"- Active quality floor: `{active_floor:g}`",
        f"- README/presentation floor: `{presentation_floor:g}`",
        f"- Status: {status}",
        "",
        "| Category | Score | Required | Gap | Next upgrade action |",
        "|---|---:|---:|---|---|",
    ]
    if gap_rows:
        for cells in gap_rows:
            lines.append("| " + " | ".join(cells) + " |")
    else:
        lines.append("| - | - | - | 없음 | floor ratchet 후 다음 프로젝트 기준으로 유지 |")

    lines.extend(
        [
            "",
            "### 다음 검증 명령",
            "",
            "```bash",
            f"python3 /workspace/prj/personal/data-scientist-career/scripts/validate_weekend_project.py --project {project} --stage sunday",
            f"python3 /workspace/prj/personal/data-scientist-career/scripts/update_quality_floor.py --quality-gate {quality_gate}",
            "```",
            END_MARKER,
        ]
    )
    return "\n".join(lines) + "\n", len(gap_rows)


def replace_auto_section(existing: str, section: str) -> str:
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(existing):
        return pattern.sub(section, existing).rstrip() + "\n"
    return existing.rstrip() + "\n\n" + section


def main() -> int:
    args = parse_args()
    quality_gate = Path(args.quality_gate)
    state_file = Path(args.state_file)
    project = infer_project_path(
        quality_gate=quality_gate,
        registry=Path(args.registry),
        source_root=Path(args.source_root),
        explicit_project=args.project,
    )
    gap_report = project / "docs/research_gap_report.md"
    active_floor = load_active_floor(state_file)
    rows = load_quality_rows(quality_gate)
    section, gap_count = build_gap_section(
        quality_gate=quality_gate,
        active_floor=active_floor,
        project=project,
        rows=rows,
    )

    payload = {
        "quality_gate": str(quality_gate),
        "state_file": str(state_file),
        "project": str(project),
        "gap_report": str(gap_report),
        "active_floor": active_floor,
        "gap_count": gap_count,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        payload["action"] = "would_update"
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    if not gap_report.is_file():
        gap_report.parent.mkdir(parents=True, exist_ok=True)
        existing = "# Research Gap Report\n"
    else:
        existing = read_text(gap_report)
    gap_report.write_text(replace_auto_section(existing, section), encoding="utf-8")
    payload["action"] = "updated"
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
