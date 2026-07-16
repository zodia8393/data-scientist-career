import csv
import importlib.util
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_decisionops_suite.py"
SPEC = importlib.util.spec_from_file_location("verify_decisionops_suite", SCRIPT)
verifier = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


def write_quality(path: Path, rows: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "score", "rationale"])
        writer.writeheader()
        for category, score in rows:
            writer.writerow({"category": category, "score": score, "rationale": "ok"})


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_bike_share_artifacts(
    artifact_path: Path,
    *,
    earliest_ready_at: str | None,
    snapshot_count: int = 268,
) -> None:
    payloads = {
        "station_level/reports/station_snapshot_readiness.json": {
            "ready_for_prospective_validation": False,
            "snapshot_count": snapshot_count,
            "min_required_snapshots": 268,
            "target_snapshots": 336,
            "earliest_ready_at": earliest_ready_at,
        },
        "station_level/reports/station_public_deploy_readiness.json": {"decision": "NO_GO"},
        "station_level/reports/station_prospective_validation.json": {
            "validation_status": "NOT_READY"
        },
        "seoul_ddareungi/reports/validation_summary.json": {
            "validation_status": "READY",
            "snapshot_count": 24,
            "min_snapshots_for_validation": 24,
        },
        "seoul_ddareungi/reports/latest_inventory_snapshot_summary.json": {
            "row_count": 10,
            "unique_station_count": 10,
        },
        "seoul_ddareungi/reports/rebalancing_priority_summary.json": {
            "priority_rows": 5,
            "action_counts": {},
        },
    }
    for relative, payload in payloads.items():
        path = artifact_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


def station_readiness_issue(artifact_path: Path, current_time: datetime) -> verifier.Issue:
    issues: list[verifier.Issue] = []
    verifier.evaluate_bike_share(artifact_path, issues, current_time=current_time)
    return next(issue for issue in issues if issue.check == "station_prospective_readiness")


def test_parse_quality_scores_accepts_decimal_scores(tmp_path):
    quality = tmp_path / "quality_gate_scores.csv"
    write_quality(quality, [("a", "95.2"), ("b", "94.2")])

    parsed = verifier.parse_quality_scores(quality)

    assert parsed["min_score"] == 94.2
    assert parsed["min_category"] == "b"


def test_station_readiness_is_pending_before_earliest_time(tmp_path):
    earliest = datetime.fromisoformat("2026-07-13T14:04:57+09:00")
    write_bike_share_artifacts(tmp_path, earliest_ready_at=earliest.isoformat())

    issue = station_readiness_issue(tmp_path, earliest - timedelta(seconds=1))

    assert issue.severity == "pending"


def test_station_readiness_is_error_at_earliest_time(tmp_path):
    earliest = datetime.fromisoformat("2026-07-13T14:04:57+09:00")
    write_bike_share_artifacts(tmp_path, earliest_ready_at=earliest.isoformat())

    issue = station_readiness_issue(tmp_path, earliest)

    assert issue.severity == "error"


def test_station_readiness_keeps_count_only_error_without_earliest_time(tmp_path):
    now = datetime.fromisoformat("2026-07-10T18:00:00+09:00")
    write_bike_share_artifacts(tmp_path, earliest_ready_at=None)

    issue = station_readiness_issue(tmp_path, now)

    assert issue.severity == "error"


def test_station_readiness_reports_malformed_earliest_time_without_losing_details(tmp_path):
    now = datetime.fromisoformat("2026-07-10T18:00:00+09:00")
    write_bike_share_artifacts(tmp_path, earliest_ready_at="not-a-timestamp")
    issues: list[verifier.Issue] = []

    details = verifier.evaluate_bike_share(tmp_path, issues, current_time=now)

    timestamp_issue = next(issue for issue in issues if issue.check == "station_earliest_ready_at")
    assert timestamp_issue.severity == "error"
    assert "not-a-timestamp" in timestamp_issue.detail
    assert details["station_snapshot_count"] == 268


def test_markdown_status_marks_expected_pending_without_warning():
    status = {
        "generated_at_kst": "2026-07-03T10:00:00+09:00",
        "ok": True,
        "summary": {"error_count": 0, "warning_count": 0, "pending_count": 1},
        "projects": [
            {
                "slug": "bike-share-demand-resilience",
                "quality": {"min_score": 92.0},
                "git": {"ok": True, "has_remote": True},
                "details": {
                    "station_snapshot_count": 94,
                    "station_min_required_snapshots": 268,
                    "seoul_snapshot_count": 6,
                    "seoul_min_snapshots_for_validation": 24,
                    "seoul_validation_status": "NOT_READY",
                },
                "issues": [{"severity": "pending"}],
            }
        ],
        "issues": [
            {
                "severity": "pending",
                "project": "bike-share-demand-resilience",
                "check": "seoul_validation",
                "detail": "status=NOT_READY, snapshots=6/24",
            }
        ],
    }

    text = verifier.markdown_status(status)

    assert "Overall: `OK`" in text
    assert "Seoul 6/24 NOT_READY" in text
    assert "Warnings: `0`" in text
    assert "Pending gates: `1`" in text
    assert "`bike-share-demand-resilience` `seoul_validation`" in text


def test_write_outputs_creates_json_and_markdown(tmp_path):
    status = {
        "generated_at_kst": "2026-07-03T10:00:00+09:00",
        "ok": True,
        "summary": {"error_count": 0, "warning_count": 0},
        "projects": [],
        "issues": [],
    }
    status_json = tmp_path / "state/status.json"
    status_md = tmp_path / "state/status.md"

    verifier.write_outputs(status, status_json, status_md)

    assert json.loads(status_json.read_text(encoding="utf-8"))["ok"] is True
    assert "DecisionOps Suite Status" in status_md.read_text(encoding="utf-8")


def test_decisionops_suite_slug_filter_is_explicit():
    assert verifier.DECISIONOPS_SUITE_SLUGS == {
        "bike-share-demand-resilience",
        "agentic-decisionops-workbench",
        "decisionops-control-tower",
    }
    assert "job-market-intelligence" not in verifier.DECISIONOPS_SUITE_SLUGS


def test_registry_keeps_job_market_intelligence_on_career_track():
    registry = json.loads(verifier.DEFAULT_REGISTRY.read_text(encoding="utf-8"))
    job_market = next(item for item in registry["projects"] if item["slug"] == "job-market-intelligence")

    assert job_market["portfolio_track"] == "career_transition_tool"
    assert job_market["decisionops_suite"] is False


def test_control_tower_pending_gate_reports_actual_auth_blocker(tmp_path):
    write_json(
        tmp_path / "reports/deployment_readiness.json",
        {
            "decisions": {
                "local_private_demo": "GO",
                "container_demo": "GO",
                "hosted_private_demo": "NO_GO",
                "public_deploy": "NO_GO",
            },
            "blockers": {
                "public_deploy": ["write auth credentials are not configured"]
            },
            "control_state": {
                "demo_mode_ready": True,
                "public_deploy_decision": "GO",
            },
        },
    )
    write_json(tmp_path / "reports/run_summary.json", {"metrics": {}})
    issues: list[verifier.Issue] = []

    details = verifier.evaluate_control_tower(tmp_path, issues)

    pending = next(issue for issue in issues if issue.check == "public_deploy")
    assert pending.severity == "pending"
    assert "write auth credentials are not configured" in pending.detail
    assert details["upstream_public_claim_decision"] == "GO"
    assert details["public_endpoint_deploy_decision"] == "NO_GO"


def test_suite_contracts_detect_stale_workbench_surfaces(tmp_path):
    bike = tmp_path / "bike"
    workbench = tmp_path / "workbench"
    tower = tmp_path / "tower"
    write_json(
        bike / "station_level/reports/station_public_deploy_readiness.json",
        {"decision": "GO"},
    )
    write_json(
        workbench / "data/processed/bike_share_decision_surface.json",
        {"deployment": {"decision": "NO_GO"}},
    )
    write_json(
        workbench / "data/processed/seoul_impact_decision_surface.json",
        {"summary": {"public_claim_state": "blocked_until_public_deploy_ready"}},
    )
    write_json(
        workbench / "reports/prepublish_audit.json",
        {"status": "public_ready"},
    )
    write_json(
        tower / "reports/impact_cards.json",
        [
            {
                "public_claim_state": "allowed",
                "guardrail_state": "ready_for_review",
            }
        ],
    )
    write_json(
        tower / "reports/control_state.json",
        {
            "source_status": {
                "workbench_prepublish_status": "public_ready",
                "bike_public_deploy_decision": "GO",
            }
        },
    )
    projects = [
        {"slug": "bike-share-demand-resilience", "artifact_path": str(bike), "issues": []},
        {"slug": "agentic-decisionops-workbench", "artifact_path": str(workbench), "issues": []},
        {"slug": "decisionops-control-tower", "artifact_path": str(tower), "issues": []},
    ]

    verifier.evaluate_suite_contracts(projects)

    checks = {item["check"] for item in projects[1]["issues"]}
    assert checks == {
        "suite_contract:bike_deploy_decision",
        "suite_contract:impact_public_claim_state",
    }


def test_suite_contracts_accept_matching_state_vocabularies(tmp_path):
    bike = tmp_path / "bike"
    workbench = tmp_path / "workbench"
    tower = tmp_path / "tower"
    write_json(
        bike / "station_level/reports/station_public_deploy_readiness.json",
        {"decision": "GO"},
    )
    write_json(
        workbench / "data/processed/bike_share_decision_surface.json",
        {"deployment": {"decision": "GO"}},
    )
    write_json(
        workbench / "data/processed/seoul_impact_decision_surface.json",
        {"summary": {"public_claim_state": "ready_for_claim"}},
    )
    write_json(
        workbench / "reports/prepublish_audit.json",
        {"status": "public_ready"},
    )
    write_json(
        tower / "reports/impact_cards.json",
        [
            {
                "public_claim_state": "allowed",
                "guardrail_state": "ready_for_review",
            }
        ],
    )
    write_json(
        tower / "reports/control_state.json",
        {
            "source_status": {
                "workbench_prepublish_status": "public_ready",
                "bike_public_deploy_decision": "GO",
            }
        },
    )
    projects = [
        {"slug": "bike-share-demand-resilience", "artifact_path": str(bike), "issues": []},
        {"slug": "agentic-decisionops-workbench", "artifact_path": str(workbench), "issues": []},
        {"slug": "decisionops-control-tower", "artifact_path": str(tower), "issues": []},
    ]

    verifier.evaluate_suite_contracts(projects)

    assert all(not project["issues"] for project in projects)
