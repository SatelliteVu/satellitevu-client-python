from http.client import HTTPResponse
from json import dumps, loads
from sys import version_info
from typing import Any, Dict, Iterable, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import AbstractClient
from .base import ResponseWrapper as BaseResponse


class ResponseWrapper(BaseResponse):
    raw: HTTPResponse

    def __init__(self, raw: HTTPResponse):
        self.raw = raw
        self.status = raw.status
        self.headers = {k: v for k, v in raw.getheaders()}

    def json(self):
        return loads(self.raw.read().decode("utf-8"))

    @property
    def text(self):
        return self.raw.read().decode("utf-8")


class UrllibClient(AbstractClient):
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
        headers = self.prepare_headers(url, headers, scopes)
        body = None
        if data:
            body = urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif json:
            body = dumps(json).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(method=method, url=url, data=body, headers=headers)
        try:
            response = urlopen(request)
        except HTTPError as error:
            response = error

        wrapper = ResponseWrapper(raw=response)
        return wrapper

    @property
    def user_agent(self) -> str:
        return f"Python-urllib/{version_info[0]}.{version_info[1]}"
