from base64 import b64decode
from datetime import datetime
from json import loads
from logging import getLogger
from typing import Optional
from urllib.parse import urljoin

from satellitevu.config import AUDIENCE, AUTH_URL
from satellitevu.http import AbstractClient, UrllibClient

from .cache import AbstractCache, AppDirCache

logger = getLogger(__file__)


def is_expired_token(token: str) -> bool:
    json = b64decode(token.split(".")[1] + "==")
    claims = loads(json)
    if not claims or "exp" not in claims:
        return False
    exp = float(claims["exp"])
    exp_dt = datetime.fromtimestamp(exp)
    return exp_dt <= datetime.now()


class AuthError(RuntimeError):
    pass


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

    def token(self) -> str:
        token = self.cache.load(self.client_id)

        if not token or is_expired_token(token):
            token = self._auth()
            self.cache.save(self.client_id, token)

        return token

    def _auth(self) -> str:
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
            },
        )

        if response.status != 200:
            raise AuthError(
                f"Unexpected error code for client_credential flow: {response.status}"
            )
        try:
            payload = response.json()
            return payload["access_token"]
        except Exception:
            raise AuthError(
                "Unexpected response body for client_credential flow: " + response.text
            )
