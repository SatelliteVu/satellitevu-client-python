from abc import ABC
from urllib.parse import urljoin
from warnings import simplefilter, warn

from satellitevu.auth.exc import Api401Error, Api403Error
from satellitevu.http import AbstractClient


class AbstractApi(ABC):
    client: AbstractClient
    base_url: str
    api_path: str
    scopes = []
    max_auth_retries: int

    def __init__(
        self, client: AbstractClient, base_url: str, max_auth_retries: int = 1
    ):
        """
        Initialize API client.

        Args:
            client: HTTP client implementation
            base_url: Base URL for API endpoints
            max_auth_retries: Maximum number of times to retry a request after 401 error.
                            When a 401 is received, the cached token is invalidated and
                            the request is retried with a fresh token. Default is 1.
        """
        self.client = client
        self.base_url = base_url
        self.max_auth_retries = max_auth_retries

    def url(self, path: str) -> str:
        api_base_url = urljoin(self.base_url, self.api_path.lstrip("/"))
        if api_base_url[-1] != "/":
            api_base_url += "/"
        return urljoin(api_base_url, path.lstrip("/"))

    def make_request(self, *args, **kwargs):
        """
        Make an HTTP request with automatic 401 retry.

        When a 401 Unauthorized response is received, this method will:
        1. Invalidate the cached authentication token
        2. Retry the request (up to max_auth_retries times)
        3. The retry will automatically fetch a fresh token via refresh or re-auth

        Args:
            *args: Positional arguments passed to client.request()
            **kwargs: Keyword arguments passed to client.request()

        Returns:
            Response object from the HTTP client

        Raises:
            Api401Error: If request is unauthorized after all retries
            Api403Error: If request is forbidden (no retry)
        """
        if "scopes" not in kwargs:
            kwargs["scopes"] = self.scopes

        for attempt in range(self.max_auth_retries + 1):
            response = self.client.request(*args, **kwargs)

            if response.status == 401:
                if attempt < self.max_auth_retries:
                    self._invalidate_auth_token(kwargs.get("scopes"))
                    continue
                else:
                    raise Api401Error("Unauthorized to make this request after retry.")
            elif response.status == 403:
                raise Api403Error(
                    (
                        "Not permitted to perform this action. "
                        "Please contact Satellite Vu for assistance."
                    )
                )

            return response

    def _invalidate_auth_token(self, scopes):
        """
        Invalidate the cached authentication token.

        This forces the next request to fetch a fresh token.

        Args:
            scopes: Scopes associated with the token to invalidate
        """
        auth = next(
            (v for k, v in self.client._auth.items() if self.base_url.startswith(k)),
            None,
        )
        if auth:
            auth.invalidate_token(scopes)

    def deprecation_warning(self, new_cls):
        simplefilter("always", DeprecationWarning)
        warn(
            f"\n{self.__class__.__name__} is deprecated in favour of "
            f"{new_cls.__name__} and will be removed in an upcoming version.\n",
            DeprecationWarning,
        )
