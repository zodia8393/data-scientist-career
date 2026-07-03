from __future__ import annotations

import os
import time
from typing import Any

import requests

from ..errors import MissingCredentialError
from ..models import RawResult, utc_now_iso
from .base import Provider


class SaraminProvider(Provider):
    name = "saramin"
    endpoint = "https://oapi.saramin.co.kr/job-search"

    def __init__(
        self,
        access_key: str | None = None,
        timeout: float = 15.0,
        retries: int = 2,
        session: requests.Session | None = None,
    ) -> None:
        self.access_key = access_key or os.getenv("SARAMIN_ACCESS_KEY")
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()

    def collect(self, limit: int = 100, query: str | None = None) -> RawResult:
        if not self.access_key:
            raise MissingCredentialError("SARAMIN_ACCESS_KEY is not configured.")

        jobs: list[dict[str, Any]] = []
        page = 0
        keyword = query or "Data Scientist 데이터 사이언티스트 ML Engineer Applied AI"
        while len(jobs) < limit:
            page_size = min(110, limit - len(jobs))
            payload = self._request_page(keyword=keyword, start=page, count=page_size)
            page_jobs = self._extract_jobs(payload)
            if not page_jobs:
                break
            jobs.extend(page_jobs)
            if len(page_jobs) < page_size:
                break
            page += 1
            time.sleep(0.2)
        return RawResult(
            provider=self.name,
            mode="api",
            payload={"jobs": {"job": jobs}, "query": keyword, "provider": self.name},
            fetched_at=utc_now_iso(),
        )

    def _request_page(self, keyword: str, start: int, count: int) -> dict[str, Any]:
        params = {
            "access-key": self.access_key,
            "keywords": keyword,
            "start": start,
            "count": count,
            "sort": "pd",
            "fields": "posting-date expiration-date count",
        }
        headers = {"Accept": "application/json"}
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(
                    self.endpoint,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
                if "result" in payload:
                    result = payload["result"]
                    code = result.get("code")
                    message = result.get("message", "unknown Saramin API error")
                    raise RuntimeError(f"Saramin API error {code}: {message}")
                return payload
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"Saramin API request failed: {last_error}") from last_error

    @staticmethod
    def _extract_jobs(payload: dict[str, Any]) -> list[dict[str, Any]]:
        jobs = payload.get("jobs", {})
        if not isinstance(jobs, dict):
            return []
        job = jobs.get("job", [])
        if isinstance(job, dict):
            return [job]
        if isinstance(job, list):
            return [item for item in job if isinstance(item, dict)]
        return []
