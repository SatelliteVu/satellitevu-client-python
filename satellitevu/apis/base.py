from abc import ABC
from urllib.parse import urljoin

from satellitevu.http import AbstractClient


class AbstractApi(ABC):
    client: AbstractClient
    base_url: str
    api_path: str

    def __init__(self, client: AbstractClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def _url(self, path: str) -> str:
        api_base_url = urljoin(self.base_url, self._api_path.lstrip("/"))
        if api_base_url[-1] != "/":
            api_base_url += "/"
        return urljoin(api_base_url, path.lstrip("/"))
