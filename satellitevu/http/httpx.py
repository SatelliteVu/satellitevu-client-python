from ast import Dict
from typing import Any, Optional

from httpx import Client, Response

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
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Any] = None
    ) -> ResponseWrapper:
        headers = headers or {}

        self._set_auth(url, headers)
        response = self.client.request(
            method=method, url=url, headers=headers, data=data, json=json
        )
        return ResponseWrapper(response)
