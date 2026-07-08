import csv
import importlib.util
import json
import sys
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


def test_parse_quality_scores_accepts_decimal_scores(tmp_path):
    quality = tmp_path / "quality_gate_scores.csv"
    write_quality(quality, [("a", "95.2"), ("b", "94.2")])

    parsed = verifier.parse_quality_scores(quality)

    assert parsed["min_score"] == 94.2
    assert parsed["min_category"] == "b"


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
