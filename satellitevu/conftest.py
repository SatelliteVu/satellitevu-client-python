from importlib import import_module
from json import dumps
from typing import Dict, Optional
from urllib.parse import urljoin

from mocket.mockhttp import Entry
from pytest import fixture, mark, param

try:
    from requests import Session as RequestsSession
except ImportError:
    RequestsSession = None
try:
    from httpx import Client as HttpxClient
except ImportError:
    HttpxClient = None

from satellitevu.auth.cache import AbstractCache
from satellitevu.client import Client


@fixture(
    params=(
        param("UrllibClient"),
        param(
            "requests.RequestsSession",
            marks=[
                mark.skipif(RequestsSession is None, reason="requests is not installed")
            ],
        ),
        param(
            "httpx.HttpxClient",
            marks=[mark.skipif(HttpxClient is None, reason="httpx is not installed")],
        ),
    )
)
def http_client_class(request):
    full_path = f"satellitevu.http.{request.param}"
    module = import_module(full_path.rsplit(".", maxsplit=1)[0])
    return getattr(module, full_path.rsplit(".")[-1])


class MemoryCache(AbstractCache):
    cache: Dict[str, str]

    def __init__(self):
        super().__init__()
        self.cache = {}

    def save(self, client_id: str, value: str):
        self.cache[client_id] = value

    def load(self, client_id: str) -> Optional[str]:
        return self.cache.get(client_id)


@fixture
def client(memory_cache):
    return Client(client_id="mock-id", client_secret="mock-secret", cache=memory_cache)


@fixture
def memory_cache():
    return MemoryCache()


@fixture
def oauth_token_entry(client):
    return Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "mock-token"}),
    )


@fixture
def redirect_response():
    return {"url": "https://image.test"}


@fixture
def order_details_response():
    return {
        "id": "528b0f77-5df1-4ed7-9224-502817170613",
        "type": "FeatureCollection",
        "features": [
            {
                "id": "8566d747-8833-44a7-a1c8-8d13e541f673",
                "properties": {
                    "item_id": "image",
                    "owned_by": "random",
                    "created_at": "2022-10-20T09:23:14.959823",
                    "updated_at": "2022-10-20T09:23:14.959823",
                },
            }
        ],
    }
