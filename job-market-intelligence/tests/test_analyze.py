from datetime import datetime

from job_market_intel.analyze import analyze_jobs
from job_market_intel.models import JobPosting


def test_analyze_distinguishes_recent_postings_from_deadline_window():
    jobs = [
        JobPosting(
            source="fixture",
            external_id="1",
            company="A",
            title="Data Scientist",
            url="https://example.com/a",
            posted_at="2026-07-01T09:00:00+09:00",
            deadline_at="2026-07-10T23:59:59+09:00",
        )
    ]

    analysis = analyze_jobs(jobs, today=datetime(2026, 7, 3, 12, 0, 0))

    assert analysis["recent_posting_count"] == 1
    assert analysis["deadline_soon_count"] == 1
