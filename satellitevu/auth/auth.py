from base64 import b64decode
from datetime import datetime
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


def is_expired_token(token: str) -> bool:
    json = b64decode(token.split(".")[1] + "==")
    claims = loads(json)
    if not claims or "exp" not in claims:
        return False
    exp = float(claims["exp"])
    exp_dt = datetime.fromtimestamp(exp)
    return exp_dt <= datetime.now()


class Auth:
    client_id: str
    client_secret: str
    audience: str

    cache: AbstractCache

    auth_url: str
    client: AbstractClient

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        audience: Optional[str] = None,
        cache: Optional[AbstractCache] = None,
        auth_url: Optional[str] = None,
        client: Optional[AbstractClient] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience or AUDIENCE

        self.cache = cache or AppDirCache()
        self.auth_url = auth_url or AUTH_URL
        self.client = client or UrllibClient()

    def token(self, scopes: Optional[List] = None) -> str:
        if not scopes:
            scopes = []
        cache_key = sha1(self.client_id.encode("utf-8"))  # nosec B324
        cache_key.update("".join(scopes).encode("utf-8"))

        token = self.cache.load(cache_key.hexdigest())

        if not token or is_expired_token(token):
            token = self._auth(scopes)
            self.cache.save(cache_key.hexdigest(), token)

        return token

    def _auth(self, scopes: Optional[List] = None) -> str:
        if not scopes:
            scopes = []
        logger.info("Performing client_credential authentication")
        token_url = urljoin(self.auth_url, "oauth/token")
        response = self.client.post(
            token_url,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
                "scope": " ".join(scopes),
            },
        )

        if response.status != 200:
            raise AuthError(
                "Unexpected error code for client_credential flow: "
                f"{response.status} - {response.text}"
            )
        try:
            payload = response.json()
            return payload["access_token"]
        except Exception:
            raise AuthError(
                "Unexpected response body for client_credential flow: " + response.text
            )
