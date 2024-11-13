from calendar import timegm
from datetime import datetime, timedelta, timezone
from importlib import import_module
from json import dumps
from typing import Dict, Optional, Callable
from urllib.parse import urljoin
from uuid import uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from josepy import JWKRSA
from jwt import PyJWK, encode
from mocket import mocketize
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
def oauth_token_entry(client, auth0_token_factory) -> str:
    token = auth0_token_factory("John Doe")
    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": token}),
    )
    return f"Bearer {token}"


@fixture(scope="session")
def jwk():
    key = generate_private_key(
        backend=default_backend,
        public_exponent=65537,
        key_size=1024,
    ).private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        NoEncryption(),
    )
    return JWKRSA.load(key).to_json()


@fixture(scope="session")
def auth_url() -> str:
    return "http://auth.example.com"


@mocketize(strict_mode=True)
@fixture(scope="function")
def generic_token_factory(
    jwk,
    auth_url,
) -> Callable[..., str]:
    def factory(ttl=300, **claims):
        """
        Generate JWT for given claims with a given TTL, signed with the provider's RSA
        key.
        """
        now = timegm(datetime.now(tz=timezone.utc).utctimetuple())
        payload = {
            **claims,
            "iat": now,
            "exp": now + ttl,
        }
        jwk_obj = PyJWK(jwk, algorithm="RS256")
        return encode(payload, jwk_obj.key, algorithm=jwk_obj.algorithm_name)

    return factory


@fixture(scope="function")
def auth0_token_factory(generic_token_factory):
    def factory(name: str, *, ttl=300, **access_claims):
        given, family = name.split(" ")
        return generic_token_factory(
            ttl=ttl,
            iss=access_claims.pop("iss", "test"),
            azp="test",
            sub=f"{given.lower()}_{family.lower()}",
            scope=access_claims.pop("scope", "openid"),
            **access_claims,
        )

    return factory


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
    now = datetime.now(timezone.utc)
    return {
        "coordinates": [0, 0],
        "date_from": now,
        "date_to": (now + timedelta(hours=24)),
        "day_night_mode": "night",
        "max_cloud_cover": 100,
        "min_off_nadir": 20,
        "max_off_nadir": 30,
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
            "status": "feasible",
        },
        "id": str(uuid4()),
        "contract_id": str(otm_request_parameters["contract_id"]),
        "links": [],
    }


@fixture
def search_response(otm_request_parameters):
    return {
        "type": "FeatureCollection",
        "features": [
            {
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
                    "status": "feasible",
                    "max_gsd": 6.8,
                    "min_gsd": 3.5,
                    "max_off_nadir": 45,
                    "min_off_nadir": 0,
                    "day_night_mode": "day",
                    "max_cloud_cover": None,
                    "created_at": "2023-10-06T08:56:26.760670",
                    "updated_at": "2023-10-06T08:56:28.686189",
                },
                "id": "57645c80-fda4-4116-9270-6f1b2a097000",
                "contract_id": "74841d4e-60d4-4e73-a691-2dddffa10d92",
                "collection": "feasibility",
            },
        ],
        "context": {"limit": 25, "matched": 1, "returned": 1},
        "links": [],
    }
