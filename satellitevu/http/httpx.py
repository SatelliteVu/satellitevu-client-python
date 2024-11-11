from typing import Any, Dict, Iterable, Optional

from httpx import Client, Response
from httpx.__version__ import __version__

from .base import AbstractClient
from .base import ResponseWrapper as BaseResponse


class ResponseWrapper(BaseResponse):
    raw: Response

    def __init__(self, raw: Response):
        self.raw = raw
        self.status = raw.status_code
        self.headers = raw.headers

    def json(self):
        return self.raw.json()

    @property
    def text(self):
        return self.raw.text


class HttpxClient(AbstractClient):
    client: Client

    def __init__(self, instance: Optional[Client] = None):
        super().__init__()
        self.client = instance or Client()

    def request(
        self,
        method: str,
        url: str,
        *,
        scopes: Optional[Iterable[str]] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Any] = None,
    ) -> ResponseWrapper:
        response = self.client.request(
            method=method,
            url=url,
            headers=self.prepare_headers(url, headers, scopes),
            data=data,
            json=json,
        )
        return ResponseWrapper(response)

    @property
    def user_agent(self) -> str:
        return f"python-httpx/{__version__}"
