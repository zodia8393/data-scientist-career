from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .skills import canonical_skill_set


REQUIRED_PROFILE_KEYS = {
    "target_roles",
    "preferred_locations",
    "skills",
    "projects",
    "domains",
    "avoid_keywords",
    "min_salary_optional",
}


def load_profile(path: Path | str, project_root: Path | str = ".") -> dict[str, Any]:
    profile_path = Path(path)
    if not profile_path.is_absolute():
        profile_path = Path(project_root).resolve() / profile_path
    if not profile_path.exists() and profile_path.name == "profile.yaml":
        workspace_example = Path(project_root).resolve() / "profile.example.yaml"
        package_example = Path(__file__).resolve().parents[1] / "profile.example.yaml"
        profile_path = workspace_example if workspace_example.exists() else package_example
    if not profile_path.exists():
        raise FileNotFoundError(f"profile not found: {profile_path}")

    data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    missing = sorted(REQUIRED_PROFILE_KEYS - set(data))
    if missing:
        raise ValueError(f"profile is missing required keys: {', '.join(missing)}")
    data["skills"] = sorted(canonical_skill_set(data.get("skills", [])), key=str.lower)
    data["domains"] = [str(item).lower() for item in data.get("domains", [])]
    data["target_roles"] = [str(item).lower() for item in data.get("target_roles", [])]
    data["preferred_locations"] = [str(item).lower() for item in data.get("preferred_locations", [])]
    data["avoid_keywords"] = [str(item).lower() for item in data.get("avoid_keywords", [])]
    return data
