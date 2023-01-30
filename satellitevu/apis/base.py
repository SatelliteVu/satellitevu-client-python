from abc import ABC
from urllib.parse import urljoin

from satellitevu.auth.exc import Api401Error, Api403Error
from satellitevu.http import AbstractClient


class AbstractApi(ABC):
    client: AbstractClient
    base_url: str
    api_path: str
    scopes = []

    def __init__(self, client: AbstractClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def url(self, path: str) -> str:
        api_base_url = urljoin(self.base_url, self.api_path.lstrip("/"))
        if api_base_url[-1] != "/":
            api_base_url += "/"
        return urljoin(api_base_url, path.lstrip("/"))

    def make_request(self, *args, **kwargs):
        if "scopes" not in kwargs:
            kwargs["scopes"] = self.scopes
        response = self.client.request(*args, **kwargs)

        if response.status == 401:
            raise Api401Error("Unauthorized to make this request.")
        elif response.status == 403:
            raise Api403Error(
                (
                    "Not permitted to perform this action. "
                    "Please contact Satellite Vu for assistance."
                )
            )

        return response
