from job_market_intel.providers.specs import PROVIDER_SPECS


def test_provider_specs_cover_required_sources():
    for provider in ["saramin", "work24", "wanted", "jobkorea"]:
        assert provider in PROVIDER_SPECS
        assert PROVIDER_SPECS[provider].docs_url.startswith("https://")
        assert PROVIDER_SPECS[provider].credential_env
