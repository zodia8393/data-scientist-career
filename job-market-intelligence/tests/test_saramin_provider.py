from job_market_intel.providers.saramin import SaraminProvider


def test_extract_jobs_accepts_single_job_dict():
    payload = {"jobs": {"job": {"id": "1", "position": {"title": "Data Scientist"}}}}

    jobs = SaraminProvider._extract_jobs(payload)

    assert jobs == [{"id": "1", "position": {"title": "Data Scientist"}}]


def test_extract_jobs_rejects_unexpected_shape():
    assert SaraminProvider._extract_jobs({"jobs": []}) == []
