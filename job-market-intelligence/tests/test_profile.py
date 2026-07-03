from pathlib import Path

import pytest

from job_market_intel.profile import load_profile


def test_load_profile_rejects_missing_required_keys(tmp_path):
    profile_path = tmp_path / "bad.yaml"
    profile_path.write_text("skills: [Python]\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_profile(profile_path, project_root=tmp_path)
