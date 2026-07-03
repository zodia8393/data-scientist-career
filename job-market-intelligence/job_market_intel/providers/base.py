from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import RawResult


class Provider(ABC):
    name: str

    @abstractmethod
    def collect(self, limit: int = 100, query: str | None = None) -> RawResult:
        """Collect raw postings from the provider."""
