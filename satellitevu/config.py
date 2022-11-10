from os import getenv as _getenv
from typing import Optional, Union

env_prefix = "SATELLITEVU_"


def getenv(key: str, default: Optional[str] = None) -> Union[str, None]:
    """
    Get env var for given key with defined prefix
    """
    return _getenv(f"{env_prefix}{key.upper()}", default)


def boolize(value: str) -> bool:
    """
    Convert string value to meaningful boolean value
    """
    return (value or "").lower() not in ["", "0", "false", "no", "n"]


def fqdn(subdomain, use_qa=False):
    """
    Build FQDN for given subdomain and `use_qa` setting
    """
    return ".".join(
        filter(lambda x: x, [subdomain, "qa" if use_qa else None, "satellitevu.com"])
    )


"""
Set SATELLITEVU_USE_QA to a truthy value to use production endpoints by default.
Individual config values can still be overridden with their env variables.
"""
USE_QA = boolize(getenv("USE_QA", "0"))

"""
Set SATELLITEVU_API_GATEWAY to an base URL to use for all API calls. Defaults to
https://api.satellitevu.com/
"""
GATEWAY = getenv("API_GATEWAY", f"https://{fqdn('api', USE_QA)}/")

"""
Set SATELLITEVU_API_AUDIENCE to override the requested audience for tokens.
"""
AUDIENCE = getenv("API_AUDIENCE", GATEWAY)

"""
Set SATELLITEVU_AUTH_URL to override the base URL for authentication calls.
"""
AUTH_URL = getenv("AUTH_URL", f"https://{fqdn('auth', USE_QA)}/")
