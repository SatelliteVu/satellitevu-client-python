from base64 import b64decode
from datetime import datetime, timedelta
from hashlib import sha1
from json import loads
from logging import getLogger
from typing import Optional, List
from urllib.parse import urljoin

from satellitevu.config import AUDIENCE, AUTH_URL
from satellitevu.http import AbstractClient, UrllibClient

from .cache import AbstractCache, AppDirCache
from .exc import AuthError

logger = getLogger(__file__)


def is_expired_token(token: str, grace_period_seconds: int = 0) -> bool:
    """
    Check if a JWT token is expired.

    Args:
        token: JWT token string
        grace_period_seconds: Number of seconds before actual expiration to consider token expired.
                            This provides a safety buffer for network latency and clock skew.
                            Default is 0 (no grace period).

    Returns:
        True if token is expired (or within grace period of expiration), False otherwise
    """
    json = b64decode(token.split(".")[1] + "==")
    claims = loads(json)
    if not claims or "exp" not in claims:
        return False
    exp = float(claims["exp"])
    exp_dt = datetime.fromtimestamp(exp)
    grace_period = timedelta(seconds=grace_period_seconds)
    return exp_dt <= datetime.now() + grace_period


class Auth:
    client_id: str
    client_secret: str
    audience: str

    cache: AbstractCache

    auth_url: str
    client: AbstractClient
    grace_period_seconds: int
    enable_refresh: bool

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        audience: Optional[str] = None,
        cache: Optional[AbstractCache] = None,
        auth_url: Optional[str] = None,
        client: Optional[AbstractClient] = None,
        grace_period_seconds: int = 60,
        enable_refresh: bool = False,
    ):
        """
        Initialize Auth handler for OAuth2 client credentials flow.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            audience: OAuth2 audience (defaults to API gateway URL)
            cache: Cache implementation for storing tokens (defaults to AppDirCache)
            auth_url: Authentication server base URL
            client: HTTP client implementation (defaults to UrllibClient)
            grace_period_seconds: Number of seconds before token expiration to consider it expired.
                                This provides a safety buffer for network latency and clock skew.
                                Default is 60 seconds.
            enable_refresh: Enable refresh token flow. When enabled, the client will request
                          refresh tokens and use them to obtain new access tokens instead of
                          performing full re-authentication. Default is True.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience or AUDIENCE

        self.cache = cache or AppDirCache()
        self.auth_url = auth_url or AUTH_URL
        self.client = client or UrllibClient()
        self.grace_period_seconds = grace_period_seconds
        self.enable_refresh = enable_refresh

    def invalidate_token(self, scopes: Optional[List] = None):
        """
        Invalidate cached token for given scopes.

        This forces the next token() call to fetch a fresh token, either via
        refresh token or full authentication.

        Args:
            scopes: Optional list of scopes whose cached token should be invalidated
        """
        if not scopes:
            scopes = []
        cache_key = sha1(self.client_id.encode("utf-8"))  # nosec B324
        cache_key.update("".join(scopes).encode("utf-8"))
        cache_key_digest = cache_key.hexdigest()

        # Save None to invalidate the access_token cache entry
        self.cache.save(cache_key_digest, "", None)
        logger.info("Invalidated cached token")

    def token(self, scopes: Optional[List] = None) -> str:
        """
        Get a valid access token, using cache or refresh token if possible.

        Args:
            scopes: Optional list of OAuth2 scopes to request

        Returns:
            Valid access token

        Raises:
            AuthError: If authentication or token refresh fails
        """
        if not scopes:
            scopes = []
        cache_key = sha1(self.client_id.encode("utf-8"))  # nosec B324
        cache_key.update("".join(scopes).encode("utf-8"))
        cache_key_digest = cache_key.hexdigest()

        # Try to load both access and refresh tokens from cache
        access_token, refresh_token = self.cache.load_tokens(cache_key_digest)

        # Check if access token is valid
        if access_token and not is_expired_token(
            access_token, self.grace_period_seconds
        ):
            return access_token

        # Access token is expired or missing, try to refresh if we have a refresh token
        if self.enable_refresh and refresh_token:
            # Check if refresh token itself is expired (no grace period for refresh tokens)
            if not is_expired_token(refresh_token, 0):
                try:
                    logger.info("Access token expired, attempting refresh")
                    new_access_token = self._refresh(refresh_token, scopes)
                    # Keep the same refresh token (it doesn't change)
                    self.cache.save(cache_key_digest, new_access_token, refresh_token)
                    return new_access_token
                except AuthError as e:
                    # Refresh failed, fall back to full authentication
                    logger.warning(
                        f"Token refresh failed: {e}. Falling back to full authentication"
                    )

        # No refresh token, refresh failed, or refresh disabled - perform full authentication
        access_token, refresh_token = self._auth(scopes)
        self.cache.save(cache_key_digest, access_token, refresh_token)
        return access_token

    def _auth(self, scopes: Optional[List] = None) -> tuple[str, Optional[str]]:
        """
        Perform OAuth2 client credentials authentication.

        Args:
            scopes: Optional list of scopes to request

        Returns:
            Tuple of (access_token, refresh_token). refresh_token may be None if not supported
            by the server or if refresh tokens are disabled.

        Raises:
            AuthError: If authentication request fails
        """
        if not scopes:
            scopes = []
        logger.info("Performing client_credential authentication")
        token_url = urljoin(self.auth_url, "oauth/token")

        # Add offline_access scope if refresh tokens are enabled
        request_scopes = scopes.copy()
        if self.enable_refresh and "offline_access" not in request_scopes:
            request_scopes.append("offline_access")

        response = self.client.post(
            token_url,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
                "scope": " ".join(request_scopes),
            },
        )

        if response.status != 200:
            raise AuthError(
                "Unexpected error code for client_credential flow: "
                f"{response.status} - {response.text}"
            )
        try:
            payload = response.json()
            access_token = payload["access_token"]
            refresh_token = payload.get("refresh_token")
            return (access_token, refresh_token)
        except Exception:
            raise AuthError(
                "Unexpected response body for client_credential flow: " + response.text
            )

    def _refresh(self, refresh_token: str, scopes: Optional[List] = None) -> str:
        """
        Refresh access token using a refresh token.

        Args:
            refresh_token: Valid refresh token
            scopes: Optional list of scopes to request

        Returns:
            New access token

        Raises:
            AuthError: If refresh request fails
        """
        if not scopes:
            scopes = []
        logger.info("Refreshing access token using refresh token")
        token_url = urljoin(self.auth_url, "oauth/token")
        response = self.client.post(
            token_url,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "scope": " ".join(scopes),
            },
        )

        if response.status != 200:
            raise AuthError(
                "Unexpected error code for refresh_token flow: "
                f"{response.status} - {response.text}"
            )
        try:
            payload = response.json()
            return payload["access_token"]
        except Exception:
            raise AuthError(
                "Unexpected response body for refresh_token flow: " + response.text
            )
