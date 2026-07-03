from __future__ import annotations

import json
from pathlib import Path

from ..models import RawResult, utc_now_iso
from .base import Provider


class FixtureProvider(Provider):
    name = "fixture"

    def __init__(self, fixture_path: Path | None = None, provider_name: str = "fixture") -> None:
        root = Path(__file__).resolve().parents[2]
        self.fixture_path = fixture_path or root / "data" / "fixtures" / "sample_jobs.json"
        self.provider_name = provider_name

    def collect(self, limit: int = 100, query: str | None = None) -> RawResult:
        payload = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        payload["jobs"] = payload.get("jobs", [])[:limit]
        if query:
            payload["query"] = query
        return RawResult(
            provider=self.provider_name,
            mode="fixture",
            payload=payload,
            fetched_at=utc_now_iso(),
        )
