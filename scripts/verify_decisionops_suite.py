#!/usr/bin/env python3
"""Verify the three-project DecisionOps portfolio suite status."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_REGISTRY = Path("/workspace/prj/personal/data-scientist-career/registry/projects.json")
DEFAULT_STATE_DIR = Path("/DATA/HJ/prj/data-scientist-career/state")
DEFAULT_STATUS_JSON = DEFAULT_STATE_DIR / "decisionops_suite_status.json"
DEFAULT_STATUS_MD = DEFAULT_STATE_DIR / "decisionops_suite_status.md"
KST = ZoneInfo("Asia/Seoul")
DECISIONOPS_SUITE_SLUGS = frozenset(
    {
        "bike-share-demand-resilience",
        "agentic-decisionops-workbench",
        "decisionops-control-tower",
    }
)


@dataclass(frozen=True)
class Issue:
    severity: str
    project: str
    check: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "project": self.project,
            "check": self.check,
            "detail": self.detail,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--status-json", default=str(DEFAULT_STATUS_JSON))
    parser.add_argument("--status-md", default=str(DEFAULT_STATUS_MD))
    parser.add_argument("--skip-runtime", action="store_true")
    parser.add_argument(
        "--strict-runtime",
        action="store_true",
        help="Treat local health endpoint failures as errors instead of warnings.",
    )
    return parser.parse_args()


def now_kst() -> str:
    return datetime.now(KST).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(args: list[str], cwd: Path | None = None, timeout: int = 30) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def parse_quality_scores(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "score" not in rows[0]:
        raise ValueError(f"quality score file has no score rows: {path}")

    scores: list[float] = []
    min_category = ""
    for row in rows:
        score = float(str(row.get("score", "")).strip())
        scores.append(score)
        if score == min(scores):
            min_category = str(row.get("category", "")).strip()
    return {
        "path": str(path),
        "category_count": len(rows),
        "min_score": min(scores),
        "min_category": min_category,
    }


def parse_agent_success(path: Path, agent: str) -> float:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    row = next((item for item in rows if item.get("agent") == agent), None)
    if row is None:
        raise ValueError(f"agent {agent!r} is missing from {path}")
    return float(str(row.get("task_success_rate", "")).strip())


def normalize_public_claim_state(value: Any) -> str:
    state = str(value or "unknown").lower()
    if state in {"allowed", "ready", "go", "ready_for_claim"}:
        return "ready_for_claim"
    return state


def endpoint_health(url: str, timeout: float = 3.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read()
        payload: Any
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"raw_bytes": len(body)}
        return {"ok": True, "url": url, "status_code": response.status, "payload": payload}
    except Exception as exc:  # noqa: BLE001 - status report should preserve the exact local failure.
        return {"ok": False, "url": url, "error": f"{type(exc).__name__}: {exc}"}


def git_status(source_path: Path) -> dict[str, Any]:
    status = run_command(["git", "status", "--short", "--branch"], cwd=source_path)
    remote = run_command(["git", "remote", "-v"], cwd=source_path)
    return {
        "ok": status["ok"],
        "status": status["stdout"] if status["ok"] else status["stderr"],
        "has_remote": bool(remote["stdout"].strip()) if remote["ok"] else False,
        "remote": remote["stdout"] if remote["ok"] else "",
    }


def add_issue(issues: list[Issue], severity: str, project: str, check: str, detail: str) -> None:
    if severity not in {"error", "warning", "pending"}:
        raise ValueError(f"invalid severity: {severity}")
    issues.append(Issue(severity=severity, project=project, check=check, detail=detail))


def check_required_files(project: str, source_path: Path, issues: list[Issue]) -> None:
    required = [
        "README.md",
        "pyproject.toml",
        "requirements.txt",
        "scripts/run_all.sh",
        "tests/test_pipeline.py",
        "docs/data_flow_diagram.md",
        "docs/system_design.md",
    ]
    missing = [relative for relative in required if not (source_path / relative).is_file()]
    if missing:
        add_issue(issues, "error", project, "required_files", ", ".join(missing))


def evaluate_bike_share(
    artifact_path: Path,
    issues: list[Issue],
    *,
    current_time: datetime | None = None,
) -> dict[str, Any]:
    station_readiness = read_json(artifact_path / "station_level/reports/station_snapshot_readiness.json")
    public_readiness = read_json(artifact_path / "station_level/reports/station_public_deploy_readiness.json")
    prospective_validation = read_json(
        artifact_path / "station_level/reports/station_prospective_validation.json"
    )
    seoul_validation = read_json(artifact_path / "seoul_ddareungi/reports/validation_summary.json")
    seoul_inventory = read_json(artifact_path / "seoul_ddareungi/reports/latest_inventory_snapshot_summary.json")
    seoul_priority = read_json(artifact_path / "seoul_ddareungi/reports/rebalancing_priority_summary.json")

    station_ready = bool(station_readiness.get("ready_for_prospective_validation"))
    if not station_ready:
        station_count = int(station_readiness.get("snapshot_count", 0))
        min_required = int(station_readiness.get("min_required_snapshots", 268))
        before_earliest = False
        earliest_raw = station_readiness.get("earliest_ready_at")
        timestamp_valid = True
        earliest_ready_at: datetime | None = None
        if earliest_raw:
            try:
                earliest_ready_at = datetime.fromisoformat(str(earliest_raw))
            except (TypeError, ValueError):
                timestamp_valid = False
                add_issue(
                    issues,
                    "error",
                    "bike-share-demand-resilience",
                    "station_earliest_ready_at",
                    f"invalid ISO-8601 timestamp: {earliest_raw!r}",
                )

        if timestamp_valid:
            if station_count >= min_required and earliest_ready_at is not None:
                if earliest_ready_at.tzinfo is None:
                    earliest_ready_at = earliest_ready_at.replace(tzinfo=KST)
                evaluated_at = current_time or datetime.now(KST)
                if evaluated_at.tzinfo is None:
                    evaluated_at = evaluated_at.replace(tzinfo=KST)
                before_earliest = evaluated_at < earliest_ready_at
            severity = "pending" if station_count < min_required or before_earliest else "error"
            add_issue(
                issues,
                severity,
                "bike-share-demand-resilience",
                "station_prospective_readiness",
                (
                    f"{station_readiness.get('snapshot_count')}/"
                    f"{station_readiness.get('min_required_snapshots')} minimum snapshots; "
                    f"earliest_ready_at={station_readiness.get('earliest_ready_at')}"
                ),
            )

    seoul_snapshot_count = int(seoul_validation.get("snapshot_count", 0))
    seoul_min = int(seoul_validation.get("min_snapshots_for_validation", 24))
    seoul_status = str(seoul_validation.get("validation_status", "UNKNOWN"))
    if seoul_status != "READY":
        severity = "error" if seoul_snapshot_count >= seoul_min else "pending"
        add_issue(
            issues,
            severity,
            "bike-share-demand-resilience",
            "seoul_validation",
            f"status={seoul_status}, snapshots={seoul_snapshot_count}/{seoul_min}",
        )

    prospective_status = str(
        prospective_validation.get("validation_status", "UNKNOWN")
    )
    if station_ready and prospective_status != "PASS":
        add_issue(
            issues,
            "error",
            "bike-share-demand-resilience",
            "station_prospective_validation",
            f"status={prospective_status}; expected PASS after readiness",
        )

    return {
        "station_snapshot_count": station_readiness.get("snapshot_count"),
        "station_min_required_snapshots": station_readiness.get("min_required_snapshots"),
        "station_target_snapshots": station_readiness.get("target_snapshots"),
        "station_latest_snapshot_at": station_readiness.get("latest_snapshot_at"),
        "station_earliest_ready_at": station_readiness.get("earliest_ready_at"),
        "station_snapshot_cutoff_at": station_readiness.get("snapshot_cutoff_at"),
        "station_source_snapshot_count": station_readiness.get("source_snapshot_count"),
        "station_excluded_snapshot_count": station_readiness.get("excluded_snapshot_count"),
        "station_prospective_validation_status": prospective_status,
        "station_prospective_best_model": prospective_validation.get("best_model"),
        "public_deploy_decision": public_readiness.get("decision"),
        "seoul_snapshot_count": seoul_snapshot_count,
        "seoul_min_snapshots_for_validation": seoul_min,
        "seoul_validation_status": seoul_status,
        "seoul_inventory_rows": seoul_inventory.get("row_count"),
        "seoul_map_points": seoul_inventory.get("unique_station_count"),
        "seoul_priority_rows": seoul_priority.get("priority_rows"),
        "seoul_priority_action_counts": seoul_priority.get("action_counts", {}),
    }


def evaluate_workbench(artifact_path: Path, issues: list[Issue]) -> dict[str, Any]:
    prepublish = read_json(artifact_path / "reports/prepublish_audit.json")
    run_summary = read_json(artifact_path / "reports/run_summary.json")
    impact_surface = read_json(
        artifact_path / "data/processed/seoul_impact_decision_surface.json"
    )
    allowed = bool(prepublish.get("public_registry_allowed"))
    if not allowed:
        add_issue(
            issues,
            "error",
            "agentic-decisionops-workbench",
            "prepublish_audit",
            f"status={prepublish.get('status')}, public_registry_allowed={allowed}",
        )
    eval_metrics = artifact_path / "reports/eval_metrics.csv"
    holdout_metrics = artifact_path / "reports/holdout_eval_metrics.csv"
    main_success = parse_agent_success(eval_metrics, "guarded_decision_agent")
    holdout_success = parse_agent_success(holdout_metrics, "guarded_decision_agent")
    for check, value in (
        ("guarded_main_success", main_success),
        ("guarded_holdout_success", holdout_success),
    ):
        if value < 1.0:
            add_issue(
                issues,
                "error",
                "agentic-decisionops-workbench",
                check,
                f"task_success_rate={value:.3f}; expected 1.000",
            )
    return {
        "prepublish_status": prepublish.get("status"),
        "public_registry_allowed": allowed,
        "main_task_success_rate": main_success,
        "holdout_task_success_rate": holdout_success,
        "impact_public_claim_state": impact_surface.get("summary", {}).get(
            "public_claim_state"
        ),
        "impact_candidate_units_addressed": run_summary.get("impact", {}).get(
            "candidate_units_addressed"
        ),
        "eval_metrics": str(eval_metrics),
        "holdout_metrics": str(holdout_metrics),
    }


def evaluate_control_tower(artifact_path: Path, issues: list[Issue]) -> dict[str, Any]:
    deployment = read_json(artifact_path / "reports/deployment_readiness.json")
    run_summary = read_json(artifact_path / "reports/run_summary.json")
    decisions = deployment.get("decisions", {})
    blockers = deployment.get("blockers", {})
    control_state = deployment.get("control_state", {})
    if decisions.get("local_private_demo") != "GO":
        add_issue(
            issues,
            "error",
            "decisionops-control-tower",
            "deployment:local_private_demo",
            str(decisions.get("local_private_demo")),
        )
    if decisions.get("container_demo") != "GO":
        add_issue(
            issues,
            "warning",
            "decisionops-control-tower",
            "deployment:container_demo",
            f"{decisions.get('container_demo')} in current shell; verify compose runtime separately",
        )
    if decisions.get("public_deploy") != "GO":
        public_blockers = blockers.get("public_deploy", [])
        add_issue(
            issues,
            "pending",
            "decisionops-control-tower",
            "public_deploy",
            (
                f"decision={decisions.get('public_deploy')}; blockers="
                f"{'; '.join(str(item) for item in public_blockers) or 'unspecified'}"
            ),
        )
    return {
        "demo_mode_ready": control_state.get(
            "demo_mode_ready", run_summary.get("demo_mode_ready")
        ),
        "upstream_public_claim_decision": control_state.get(
            "public_deploy_decision", run_summary.get("public_deploy_decision")
        ),
        "hosted_private_deploy_decision": decisions.get("hosted_private_demo"),
        "public_endpoint_deploy_decision": decisions.get("public_deploy"),
        "public_endpoint_deploy_blockers": blockers.get("public_deploy", []),
        "review_queue_items": run_summary.get("metrics", {}).get("review_queue_items"),
        "impact_card_rows": run_summary.get("metrics", {}).get("impact_card_rows"),
        "seoul_snapshot_count": run_summary.get("metrics", {}).get("seoul_snapshot_count"),
        "deployment_decisions": decisions,
    }


def evaluate_project(
    item: dict[str, Any],
    *,
    check_runtime: bool,
    strict_runtime: bool,
) -> dict[str, Any]:
    slug = str(item["slug"])
    source_path = Path(str(item["source_path"]))
    artifact_path = Path(str(item["artifact_path"]))
    issues: list[Issue] = []

    if not source_path.is_dir():
        add_issue(issues, "error", slug, "source_path", str(source_path))
    if not artifact_path.is_dir():
        add_issue(issues, "error", slug, "artifact_path", str(artifact_path))

    if source_path.is_dir():
        check_required_files(slug, source_path, issues)

    quality: dict[str, Any] | None = None
    quality_path = artifact_path / "reports/quality_gate_scores.csv"
    if quality_path.is_file():
        quality = parse_quality_scores(quality_path)
        required = float(item.get("quality_gate_min_score", 0))
        if float(quality["min_score"]) < required:
            add_issue(
                issues,
                "error",
                slug,
                "quality_gate_min_score",
                f"min_score={quality['min_score']} < required={required}",
            )
    else:
        add_issue(issues, "error", slug, "quality_gate_scores", str(quality_path))

    git = git_status(source_path) if source_path.is_dir() else {"ok": False}
    if not git.get("ok"):
        add_issue(issues, "error", slug, "git_status", str(git.get("status", "not a git repo")))
    elif "\n" in str(git.get("status", "")) or "??" in str(git.get("status", "")):
        add_issue(issues, "warning", slug, "git_dirty", str(git.get("status", "")))
    if git.get("ok") and not git.get("has_remote"):
        add_issue(issues, "warning", slug, "git_remote", "no remote configured")

    details: dict[str, Any] = {}
    try:
        if slug == "bike-share-demand-resilience":
            details = evaluate_bike_share(artifact_path, issues)
        elif slug == "agentic-decisionops-workbench":
            details = evaluate_workbench(artifact_path, issues)
        elif slug == "decisionops-control-tower":
            details = evaluate_control_tower(artifact_path, issues)
    except Exception as exc:  # noqa: BLE001 - status report should keep evaluating the suite.
        add_issue(issues, "error", slug, "project_specific_artifacts", f"{type(exc).__name__}: {exc}")

    runtime: dict[str, Any] = {}
    if check_runtime:
        if slug == "bike-share-demand-resilience":
            runtime["station_service_health"] = endpoint_health("http://127.0.0.1:8765/health")
        elif slug == "decisionops-control-tower":
            runtime["control_tower_health"] = endpoint_health("http://127.0.0.1:8093/health")
        for name, result in runtime.items():
            if not result.get("ok"):
                add_issue(
                    issues,
                    "error" if strict_runtime else "warning",
                    slug,
                    name,
                    str(result.get("error")),
                )

    return {
        "slug": slug,
        "status": item.get("status"),
        "source_path": str(source_path),
        "artifact_path": str(artifact_path),
        "quality": quality,
        "git": git,
        "details": details,
        "runtime": runtime,
        "issues": [issue.as_dict() for issue in issues],
    }


def add_project_issue(
    project: dict[str, Any], severity: str, check: str, detail: str
) -> None:
    issue = Issue(
        severity=severity,
        project=str(project["slug"]),
        check=check,
        detail=detail,
    )
    project.setdefault("issues", []).append(issue.as_dict())


def control_tower_claim_state(artifact_path: Path) -> str:
    cards = read_json(artifact_path / "reports/impact_cards.json")
    if not isinstance(cards, list) or not cards:
        return "unknown"
    states = [normalize_public_claim_state(item.get("public_claim_state")) for item in cards]
    blocked = [state for state in states if state.startswith("blocked")]
    if blocked:
        return blocked[0] if len(set(blocked)) == 1 else "blocked_mixed_public_claim_states"
    guardrail_states = {str(item.get("guardrail_state", "")).lower() for item in cards}
    if guardrail_states == {"ready_for_review"}:
        return "ready_for_claim"
    return "unknown"


def evaluate_suite_contracts(projects: list[dict[str, Any]]) -> None:
    by_slug = {str(project["slug"]): project for project in projects}
    bike = by_slug.get("bike-share-demand-resilience")
    workbench = by_slug.get("agentic-decisionops-workbench")
    tower = by_slug.get("decisionops-control-tower")
    if not bike or not workbench or not tower:
        return

    try:
        bike_artifact = Path(str(bike["artifact_path"]))
        workbench_artifact = Path(str(workbench["artifact_path"]))
        tower_artifact = Path(str(tower["artifact_path"]))
        bike_decision = str(
            read_json(
                bike_artifact
                / "station_level/reports/station_public_deploy_readiness.json"
            ).get("decision", "UNKNOWN")
        )
        workbench_bike_decision = str(
            read_json(
                workbench_artifact
                / "data/processed/bike_share_decision_surface.json"
            ).get("deployment", {})
            .get("decision", "UNKNOWN")
        )
        if bike_decision != workbench_bike_decision:
            add_project_issue(
                workbench,
                "error",
                "suite_contract:bike_deploy_decision",
                f"workbench={workbench_bike_decision}, upstream={bike_decision}",
            )

        workbench_claim_state = normalize_public_claim_state(
            read_json(
                workbench_artifact
                / "data/processed/seoul_impact_decision_surface.json"
            ).get("summary", {})
            .get("public_claim_state")
        )
        tower_claim_state = control_tower_claim_state(tower_artifact)
        if workbench_claim_state != tower_claim_state:
            add_project_issue(
                workbench,
                "error",
                "suite_contract:impact_public_claim_state",
                f"workbench={workbench_claim_state}, control_tower={tower_claim_state}",
            )

        tower_control_state = read_json(tower_artifact / "reports/control_state.json")
        tower_sources = tower_control_state.get("source_status", {})
        workbench_status = str(
            read_json(workbench_artifact / "reports/prepublish_audit.json").get(
                "status", "UNKNOWN"
            )
        )
        if str(tower_sources.get("workbench_prepublish_status")) != workbench_status:
            add_project_issue(
                tower,
                "error",
                "suite_contract:workbench_prepublish_status",
                (
                    f"control_tower={tower_sources.get('workbench_prepublish_status')}, "
                    f"workbench={workbench_status}"
                ),
            )
        if str(tower_sources.get("bike_public_deploy_decision")) != bike_decision:
            add_project_issue(
                tower,
                "error",
                "suite_contract:bike_public_deploy_decision",
                (
                    f"control_tower={tower_sources.get('bike_public_deploy_decision')}, "
                    f"bike_share={bike_decision}"
                ),
            )
    except Exception as exc:  # noqa: BLE001 - preserve the cross-project contract failure.
        add_project_issue(
            workbench,
            "error",
            "suite_contract:artifact_read",
            f"{type(exc).__name__}: {exc}",
        )


def build_status(
    *,
    registry: Path,
    check_runtime: bool,
    strict_runtime: bool,
) -> dict[str, Any]:
    registry_payload = read_json(registry)
    projects = [
        evaluate_project(item, check_runtime=check_runtime, strict_runtime=strict_runtime)
        for item in registry_payload.get("projects", [])
        if str(item.get("slug", "")) in DECISIONOPS_SUITE_SLUGS
    ]
    evaluate_suite_contracts(projects)
    issues = [issue for project in projects for issue in project["issues"]]
    errors = [issue for issue in issues if issue["severity"] == "error"]
    warnings = [issue for issue in issues if issue["severity"] == "warning"]
    pending = [issue for issue in issues if issue["severity"] == "pending"]
    return {
        "generated_at_kst": now_kst(),
        "registry": str(registry),
        "ok": not errors,
        "summary": {
            "project_count": len(projects),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "pending_count": len(pending),
            "runtime_checked": check_runtime,
            "strict_runtime": strict_runtime,
        },
        "projects": projects,
        "issues": issues,
    }


def markdown_status(status: dict[str, Any]) -> str:
    lines = [
        "# DecisionOps Suite Status",
        "",
        f"- Generated: `{status['generated_at_kst']}`",
        f"- Overall: `{'OK' if status['ok'] else 'CHECK_REQUIRED'}`",
        f"- Errors: `{status['summary']['error_count']}`",
        f"- Warnings: `{status['summary']['warning_count']}`",
        f"- Pending gates: `{status['summary'].get('pending_count', 0)}`",
        "",
        "| Project | Git | Quality min | Key state | Open items |",
        "|---|---|---:|---|---:|",
    ]
    for project in status["projects"]:
        quality = project.get("quality") or {}
        details = project.get("details") or {}
        git = project.get("git") or {}
        if project["slug"] == "bike-share-demand-resilience":
            key_state = (
                f"station {details.get('station_snapshot_count')}/"
                f"{details.get('station_min_required_snapshots')}, "
                f"Seoul {details.get('seoul_snapshot_count')}/"
                f"{details.get('seoul_min_snapshots_for_validation')} "
                f"{details.get('seoul_validation_status')}"
            )
        elif project["slug"] == "agentic-decisionops-workbench":
            key_state = (
                f"prepublish={details.get('prepublish_status')}, "
                f"public_allowed={details.get('public_registry_allowed')}"
            )
        elif project["slug"] == "decisionops-control-tower":
            key_state = (
                f"claim={details.get('upstream_public_claim_decision')}, "
                f"hosted={details.get('hosted_private_deploy_decision')}, "
                f"public_endpoint={details.get('public_endpoint_deploy_decision')}"
            )
        else:
            key_state = str(project.get("status"))
        git_label = "ok"
        if not git.get("ok"):
            git_label = "error"
        elif not git.get("has_remote"):
            git_label = "local"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(project["slug"]),
                    git_label,
                    f"{quality.get('min_score', 'n/a')}",
                    key_state,
                    str(len(project.get("issues", []))),
                ]
            )
            + " |"
        )

    active_issues = [issue for issue in status["issues"] if issue["severity"] != "pending"]
    pending_issues = [issue for issue in status["issues"] if issue["severity"] == "pending"]

    if active_issues:
        lines.extend(["", "## Issues", ""])
        for issue in active_issues:
            lines.append(
                f"- `{issue['severity']}` `{issue['project']}` `{issue['check']}`: {issue['detail']}"
            )
    else:
        lines.extend(["", "## Issues", "", "- 없음"])

    if pending_issues:
        lines.extend(["", "## Pending Gates", ""])
        for issue in pending_issues:
            lines.append(
                f"- `{issue['project']}` `{issue['check']}`: {issue['detail']}"
            )
    else:
        lines.extend(["", "## Pending Gates", "", "- 없음"])

    return "\n".join(lines) + "\n"


def write_outputs(status: dict[str, Any], status_json: Path, status_md: Path) -> None:
    status_json.parent.mkdir(parents=True, exist_ok=True)
    status_md.parent.mkdir(parents=True, exist_ok=True)
    status_json.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status_md.write_text(markdown_status(status), encoding="utf-8")


def main() -> int:
    args = parse_args()
    status = build_status(
        registry=Path(args.registry),
        check_runtime=not args.skip_runtime,
        strict_runtime=args.strict_runtime,
    )
    write_outputs(status, Path(args.status_json), Path(args.status_md))
    print(json.dumps(status["summary"], ensure_ascii=False))
    return 0 if status["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
