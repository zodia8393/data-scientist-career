import csv
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_weekend_project.py"
SPEC = importlib.util.spec_from_file_location("validate_weekend_project", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


def test_parse_prepublish_audit_json_blocks_failed_check(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "prepublish_audit.json").write_text(
        json.dumps(
            {
                "status": "publish_blocked",
                "public_registry_allowed": False,
                "checks": [{"check": "incident_domain_real_data", "passed": False}],
            }
        ),
        encoding="utf-8",
    )

    passed, detail = validator.parse_prepublish_audit(reports)

    assert passed is False
    assert "incident_domain_real_data" in detail
    assert "public_registry_allowed=False" in detail


def test_parse_prepublish_audit_json_allows_public_ready(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "prepublish_audit.json").write_text(
        json.dumps(
            {
                "status": "public_ready",
                "public_registry_allowed": True,
                "checks": [{"check": "holdout_guarded_success_rate", "passed": True}],
            }
        ),
        encoding="utf-8",
    )

    passed, detail = validator.parse_prepublish_audit(reports)

    assert passed is True
    assert "public_registry_allowed=True" in detail


def test_parse_prepublish_audit_csv_fallback(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    with (reports / "prepublish_audit.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "passed", "detail"])
        writer.writeheader()
        writer.writerow({"check": "unique_prompt_count", "passed": "True", "detail": "ok"})

    passed, detail = validator.parse_prepublish_audit(reports)

    assert passed is True
    assert "checks=1" in detail


def test_parse_prepublish_audit_missing_returns_none(tmp_path):
    assert validator.parse_prepublish_audit(tmp_path / "reports") is None
