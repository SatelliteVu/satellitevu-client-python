from datetime import datetime, timedelta
from importlib import import_module
from json import dumps
from typing import Dict, Optional
from urllib.parse import urljoin
from uuid import uuid4

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


@fixture
def otm_request_parameters():
    now = datetime.now().utcnow()
    return {
        "coordinates": [0, 0],
        "date_from": now,
        "date_to": (now + timedelta(hours=24)).utcnow(),
        "day_night_mode": "night",
        "max_cloud_cover": 100,
        "min_off_nadir": 0,
        "max_off_nadir": 45,
        "contract_id": str(uuid4()),
    }


@fixture
def otm_response(otm_request_parameters):
    return {
        "bbox": [0.0, 0.0, 0.0, 0.0],
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": otm_request_parameters["coordinates"],
        },
        "properties": {
            "datetime": (
                f"{otm_request_parameters['date_from']}/"
                f"{otm_request_parameters['date_to']}"
            ),
            "satvu:day_night_mode": otm_request_parameters["day_night_mode"],
            "max_cloud_cover": otm_request_parameters["max_cloud_cover"],
            "min_off_nadir": otm_request_parameters["min_off_nadir"],
            "max_off_nadir": otm_request_parameters["min_off_nadir"],
            "min_gsd": 3.5,
            "max_gsd": 6.8,
            "status": "pending",
        },
        "id": str(uuid4()),
        "contract_id": str(otm_request_parameters["contract_id"]),
        "links": [],
    }
