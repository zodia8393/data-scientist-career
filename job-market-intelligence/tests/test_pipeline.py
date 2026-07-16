import json
from pathlib import Path

import pytest

from job_market_intel.cli import collect_provider, main
from job_market_intel.errors import MissingCredentialError
from job_market_intel.normalize import normalize_raw_wrappers
from job_market_intel.profile import load_profile
from job_market_intel.providers.saramin import SaraminProvider
from job_market_intel.scoring import score_jobs
from job_market_intel.storage import Workspace, fetch_scored_jobs, row_counts


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def fixture_wrapper() -> dict:
    payload = json.loads((PROJECT_ROOT / "data" / "fixtures" / "sample_jobs.json").read_text(encoding="utf-8"))
    return {
        "provider": "fixture",
        "mode": "fixture",
        "fetched_at": "2026-07-03T00:00:00+00:00",
        "payload": payload,
    }


def test_demo_command_runs_end_to_end(tmp_path):
    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "demo",
            "--profile",
            str(PROJECT_ROOT / "profile.example.yaml"),
        ]
    )

    assert exit_code == 0
    counts = row_counts(Workspace(tmp_path))
    assert counts["normalized_jobs"] == 4
    assert counts["scored_jobs"] == 4
    assert (tmp_path / "reports" / "job_market_report.md").is_file()
    assert (tmp_path / "reports" / "job_market_report.html").is_file()
    assert (tmp_path / "reports" / "final_report.md").is_file()
    assert (tmp_path / "reports" / "model_card.md").is_file()
    assert (tmp_path / "reports" / "data_source_and_contract.md").is_file()
    summary = json.loads((tmp_path / "reports" / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "pass"
    assert summary["counts"] == {
        "raw_latest_items": 6,
        "normalized_jobs": 4,
        "scored_jobs": 4,
    }
    assert summary["quality_gate_passed"] is True


def test_normalize_filters_non_target_and_dedupes():
    result = normalize_raw_wrappers([fixture_wrapper()])

    assert result.raw_items == 6
    assert result.filtered_items == 5
    assert result.deduped_items == 4
    assert result.duplicate_items == 1
    assert all("HR Manager" not in job.title for job in result.jobs)


def test_score_jobs_produces_gap_and_profile_based_bullets():
    normalized = normalize_raw_wrappers([fixture_wrapper()])
    profile = load_profile(PROJECT_ROOT / "profile.example.yaml", project_root=PROJECT_ROOT)

    results = score_jobs(normalized.jobs, profile)

    assert results[0].fit_score >= results[-1].fit_score
    assert results[0].resume_bullets
    assert any("근거" in bullet or "구현" in bullet for bullet in results[0].resume_bullets)
    assert isinstance(results[0].skill_gap, list)


def test_saramin_provider_requires_access_key(monkeypatch):
    monkeypatch.delenv("SARAMIN_ACCESS_KEY", raising=False)

    with pytest.raises(MissingCredentialError):
        SaraminProvider().collect(limit=1)


def test_saramin_collect_uses_fixture_fallback_without_key(monkeypatch):
    monkeypatch.delenv("SARAMIN_ACCESS_KEY", raising=False)

    result = collect_provider("saramin", limit=2, query=None, fixture_fallback=True)

    assert result.provider == "saramin"
    assert result.mode == "fixture"
    assert len(result.payload["jobs"]) == 2


def test_score_command_uses_profile_example_fallback(tmp_path):
    assert main(["--workspace", str(tmp_path), "demo", "--profile", str(PROJECT_ROOT / "profile.example.yaml")]) == 0
    assert main(["--workspace", str(tmp_path), "score", "--profile", "profile.yaml"]) == 0

    scored = fetch_scored_jobs(Workspace(tmp_path))
    assert len(scored) == 4
