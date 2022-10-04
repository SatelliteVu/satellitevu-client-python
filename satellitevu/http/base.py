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

    def post(
        self, url, *, headers: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> ResponseWrapper:
        return self.request("POST", url, headers=headers, data=data)

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> ResponseWrapper:
        pass
