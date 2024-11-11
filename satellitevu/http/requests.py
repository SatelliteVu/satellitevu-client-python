from ast import Dict
from typing import Any, Iterable, Optional

from requests import Response, Session
from requests.utils import default_user_agent

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


class RequestsSession(AbstractClient):
    session: Session

    def __init__(self, instance: Optional[Session] = None):
        super().__init__()
        self.session = instance or Session()

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
        response = self.session.request(
            method=method,
            url=url,
            headers=self.prepare_headers(url, headers, scopes),
            data=data,
            json=json,
        )
        return ResponseWrapper(response)

    @property
    def user_agent(self) -> str:
        return f"{default_user_agent()}"
