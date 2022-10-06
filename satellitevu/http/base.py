from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ResponseWrapper(ABC):
    raw: Any
    headers: Dict[str, str]
    status: int
    json: Any
    text: str

    @abstractmethod
    def json(self):
        pass


class AbstractClient(ABC):
    """
    Abstract HTTP client
    """

    _auth: Dict[str, Any]

    def __init__(self):
        self._auth = {}

    def post(
        self,
        url,
        *,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Any] = None,
    ) -> ResponseWrapper:
        return self.request("POST", url, headers=headers, data=data, json=json)

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Any] = None,
    ) -> ResponseWrapper:
        pass

    def set_auth(self, base_url: str, auth):
        self._auth[base_url] = auth

    def _set_auth(self, url: str, headers):
        auth = next((v for k, v in self._auth.items() if url.startswith(k)), None)
        has_auth = next(
            (True for k in headers.keys() if k.lower() == "authorization"), False
        )
        if auth and not has_auth:
            headers["authorization"] = f"Bearer {auth.token()}"
