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


def test_resolve_required_file_path_accepts_declared_monorepo_ci(tmp_path):
    project = tmp_path / "nested-project"
    project.mkdir()
    workflow = tmp_path / ".github" / "workflows" / "nested-project-ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: ci\n", encoding="utf-8")

    resolved = validator.resolve_required_file_path(
        project,
        ".github/workflows/ci.yml",
        {"ci_workflow_path": str(workflow)},
    )

    assert resolved == workflow


def test_resolve_required_file_path_keeps_missing_local_contract(tmp_path):
    project = tmp_path / "standalone-project"
    project.mkdir()

    resolved = validator.resolve_required_file_path(
        project,
        ".github/workflows/ci.yml",
        None,
    )

    assert resolved == project / ".github/workflows/ci.yml"


def test_secret_value_regex_detects_quoted_literal_assignments():
    assert validator.SECRET_VALUE_RE.search('token = "literal-secret-value-123"')
    assert validator.SECRET_VALUE_RE.search("api_key=literal-api-key-value-123")


def test_secret_value_regex_ignores_runtime_generated_credentials():
    assert validator.SECRET_VALUE_RE.search("token = secrets.token_urlsafe(32)") is None
