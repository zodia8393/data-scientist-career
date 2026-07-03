class JobMarketIntelError(Exception):
    """Base exception for expected CLI failures."""


class MissingCredentialError(JobMarketIntelError):
    """Raised when a provider needs an API key that is not configured."""


class NoRawDataError(JobMarketIntelError):
    """Raised when normalization has no collected raw response to process."""
