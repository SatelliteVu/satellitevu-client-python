import allure
from calendar import timegm
from datetime import datetime, timedelta, timezone
from importlib import import_module
from json import dumps
from typing import Dict, Optional, Callable
from urllib.parse import urljoin
from uuid import uuid4
from collections.abc import Generator
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from josepy import JWKRSA
from jwt import PyJWK, encode
from mocket import mocketize, Mocketizer
from mocket.mockhttp import Entry
from pact.v3 import Pact
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
def order_list_response():
    return {
        "orders": [
            {
                "id": "06b45f92-f574-43e1-88ea-0725a99f69c6",
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "3749aa20-7a0a-4322-823d-b27aa5981eaf",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [23.381329637, 29.62479696],
                                    [23.324715343, 29.623895588],
                                    [23.327505896, 29.587107204],
                                    [23.384102168, 29.588120601],
                                    [23.381329637, 29.62479696],
                                ]
                            ],
                        },
                        "properties": {
                            "item_id": "20231208T115432000_visual_30_hotsat1",
                            "order_id": "06b45f92-f574-43e1-88ea-0725a99f69c6",
                            "created_at": "2024-10-18T11:05:35Z",
                            "stac_metadata": {
                                "id": "20231208T115432000_visual_30_hotsat1",
                                "collection": "visual",
                                "assets": {
                                    "thumbnail": {
                                        "href": "https://images.test.satvu.com/stac-ingestion/hotsat1/20231208T115432000_visual_30_hotsat1_thumbnail.png",
                                        "type": "image/png",
                                        "roles": ["thumbnail"],
                                    }
                                },
                                "bbox": [
                                    23.323807253417414,
                                    29.586046830070046,
                                    23.38498589650168,
                                    29.625820737625705,
                                ],
                                "properties": {
                                    "eo:cloud_cover": 0.0,
                                    "datetime": "2023-12-08T11:54:32Z",
                                    "gsd": 4.142945289611816,
                                    "platform": "hotsat-1",
                                    "view:azimuth": 284.16017649457757,
                                    "view:off_nadir": 21.334559545721035,
                                    "view:sun_azimuth": 206.56290529852637,
                                    "view:sun_elevation": 32.819692975864264,
                                },
                            },
                            "price": {"value": 2, "currency": "GBP"},
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "b16989e5-90c4-4f5f-bbad-cb5c1a0c21a6",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [17.094034765, -22.534767225],
                                    [17.09845738, -22.51733564],
                                    [17.102228197, -22.497986319],
                                    [17.046960337, -22.489298278],
                                    [17.042233475, -22.509005634],
                                    [17.039040857, -22.525958237],
                                    [17.094034765, -22.534767225],
                                ]
                            ],
                        },
                        "properties": {
                            "item_id": "20231208T120814000_visual_30_hotsat1",
                            "order_id": "06b45f92-f574-43e1-88ea-0725a99f69c6",
                            "created_at": "2024-10-18T11:05:35Z",
                            "stac_metadata": {
                                "id": "20231208T120814000_visual_30_hotsat1",
                                "collection": "visual",
                                "assets": {
                                    "thumbnail": {
                                        "href": "https://images.test.satvu.com/stac-ingestion/hotsat1/20231208T120814000_visual_30_hotsat1_thumbnail.png",
                                        "type": "image/png",
                                        "roles": ["thumbnail"],
                                    }
                                },
                                "bbox": [
                                    17.038442295262946,
                                    -22.53553050270601,
                                    17.102804643698693,
                                    -22.488568972304773,
                                ],
                                "properties": {
                                    "eo:cloud_cover": 0.0,
                                    "datetime": "2023-12-08T12:08:14Z",
                                    "gsd": 4.266286373138428,
                                    "platform": "hotsat-1",
                                    "view:azimuth": 91.71971393015937,
                                    "view:off_nadir": 24.376613013992234,
                                    "view:sun_azimuth": 265.30216497291434,
                                    "view:sun_elevation": 70.46137872028515,
                                },
                            },
                            "price": {"value": 2, "currency": "GBP"},
                        },
                    },
                ],
                "owned_by": "string",
                "created_at": "2024-10-18T11:05:35Z",
                "updated_at": "2024-10-18T11:05:35Z",
                "contract_id": "4de7e9f1-dcf1-484a-8554-a8f6bb7c22e2",
                "price": {"value": 2, "currency": "GBP"},
            },
            {
                "id": "41de67e1-cb62-45dc-aa94-b026aff9f776",
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "ed2cc9c5-625a-4fbc-8ac6-67465198e57a",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [51.322892628, 25.145864273],
                                    [51.304924939, 25.15127406],
                                    [51.28676628, 25.115093129],
                                    [51.345897132, 25.095998054],
                                    [51.364255123, 25.132339095],
                                    [51.322892628, 25.145864273],
                                ]
                            ],
                        },
                        "properties": {
                            "item_id": "20231208T102026000_visual_30_hotsat1",
                            "order_id": "41de67e1-cb62-45dc-aa94-b026aff9f776",
                            "created_at": "2024-10-04T09:56:39Z",
                            "stac_metadata": {
                                "id": "20231208T102026000_visual_30_hotsat1",
                                "collection": "visual",
                                "assets": {
                                    "thumbnail": {
                                        "href": "https://images.test.satvu.com/stac-ingestion/hotsat1/20231208T102026000_visual_30_hotsat1_thumbnail.png",
                                        "type": "image/png",
                                        "roles": ["thumbnail"],
                                    }
                                },
                                "bbox": [
                                    51.286698951221425,
                                    25.09593322503868,
                                    51.364380138663044,
                                    25.15133119478952,
                                ],
                                "properties": {
                                    "eo:cloud_cover": 0.0,
                                    "datetime": "2023-12-08T10:20:26Z",
                                    "gsd": 4.647026062011719,
                                    "platform": "hotsat-1",
                                    "view:azimuth": 95.02176620678249,
                                    "view:off_nadir": 29.182734049482512,
                                    "view:sun_azimuth": 212.39816698394057,
                                    "view:sun_elevation": 34.77974478735089,
                                },
                            },
                            "price": {"value": 3, "currency": "GBP"},
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "f983ebb8-e02d-4960-bcfc-e53df611ea74",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [33.55354294, 44.591551499],
                                    [33.561941514, 44.60597847],
                                    [33.571026516, 44.625606529],
                                    [33.495996855, 44.643580806],
                                    [33.477326556, 44.607060213],
                                    [33.551625793, 44.588978666],
                                    [33.55354294, 44.591551499],
                                ]
                            ],
                        },
                        "properties": {
                            "item_id": "20231208T115018000_visual_30_hotsat1",
                            "order_id": "41de67e1-cb62-45dc-aa94-b026aff9f776",
                            "created_at": "2024-10-04T09:56:39Z",
                            "stac_metadata": {
                                "id": "20231208T115018000_visual_30_hotsat1",
                                "collection": "visual",
                                "assets": {
                                    "thumbnail": {
                                        "href": "https://images.test.satvu.com/20231208T115018000_visual_30_hotsat1_thumbnail.png",
                                        "type": "image/png",
                                        "roles": ["thumbnail"],
                                    }
                                },
                                "bbox": [
                                    33.47715177281742,
                                    44.588782508565636,
                                    33.57122826986277,
                                    44.64367972113274,
                                ],
                                "properties": {
                                    "eo:cloud_cover": 0.0,
                                    "datetime": "2023-12-08T11:50:18Z",
                                    "gsd": 4.552684307098389,
                                    "platform": "hotsat-1",
                                    "view:azimuth": 105.29726092466655,
                                    "view:off_nadir": 28.41357725065772,
                                    "view:sun_azimuth": 211.6914436210348,
                                    "view:sun_elevation": 16.22401010212522,
                                },
                            },
                            "price": {"value": 3, "currency": "GBP"},
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "416481a9-f158-4363-b637-dd8c28ca2cb1",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [23.381329637, 29.62479696],
                                    [23.324715343, 29.623895588],
                                    [23.327505896, 29.587107204],
                                    [23.384102168, 29.588120601],
                                    [23.381329637, 29.62479696],
                                ]
                            ],
                        },
                        "properties": {
                            "item_id": "20231208T115432000_visual_30_hotsat1",
                            "order_id": "41de67e1-cb62-45dc-aa94-b026aff9f776",
                            "created_at": "2024-10-04T09:56:39Z",
                            "stac_metadata": {
                                "id": "20231208T115432000_visual_30_hotsat1",
                                "collection": "visual",
                                "assets": {
                                    "thumbnail": {
                                        "href": "https://images.test.satvu.com/stac-ingestion/hotsat1/20231208T115432000_visual_30_hotsat1_thumbnail.png",
                                        "type": "image/png",
                                        "roles": ["thumbnail"],
                                    }
                                },
                                "bbox": [
                                    23.323807253417414,
                                    29.586046830070046,
                                    23.38498589650168,
                                    29.625820737625705,
                                ],
                                "properties": {
                                    "eo:cloud_cover": 0.0,
                                    "datetime": "2023-12-08T11:54:32Z",
                                    "gsd": 4.142945289611816,
                                    "platform": "hotsat-1",
                                    "view:azimuth": 284.16017649457757,
                                    "view:off_nadir": 21.334559545721035,
                                    "view:sun_azimuth": 206.56290529852637,
                                    "view:sun_elevation": 32.819692975864264,
                                },
                            },
                            "price": {"value": 3, "currency": "GBP"},
                        },
                    },
                ],
                "owned_by": "string",
                "created_at": "2024-10-04T09:56:39Z",
                "updated_at": "2024-10-04T09:56:39Z",
                "contract_id": "4de7e9f1-dcf1-484a-8554-a8f6bb7c22e2",
                "price": {"value": 3, "currency": "GBP"},
            },
        ],
        "links": [],
    }


@fixture
def redirect_response():
    return {"url": "https://image.test", "ttl": 3600}


@fixture
def order_details_response():
    return {
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {
                    "item_id": "20231110T173102000_visual_30_hotsat",
                    "order_id": "1cfdc8cc-968d-406c-bada-d45c55a26857",
                    "created_at": "2019-08-24T14:15:22Z",
                    "stac_metadata": {
                        "id": "string",
                        "collection": "string",
                        "assets": {
                            "property1": {
                                "href": "http://example.com",
                                "type": "string",
                                "roles": ["string"],
                            },
                            "property2": {
                                "href": "http://example.com",
                                "type": "string",
                                "roles": ["string"],
                            },
                        },
                        "bbox": [0, 0, 0, 0],
                        "properties": {
                            "eo:cloud_cover": 0,
                            "datetime": "2019-08-24T14:15:22Z",
                            "gsd": 0,
                            "platform": "string",
                            "view:azimuth": 0,
                            "view:off_nadir": 0,
                            "view:sun_azimuth": 0,
                            "view:sun_elevation": 0,
                        },
                    },
                    "price": {"value": 100000, "currency": "GBP"},
                },
            }
        ],
        "owned_by": "John Doe",
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z",
        "contract_id": "9aafc1a8-e497-46c9-ba0b-bd5b03c353e4",
        "price": {"value": 100000, "currency": "GBP"},
    }


@fixture
def otm_request_parameters(withhold="0d"):
    now = datetime.now(timezone.utc)
    return {
        "addon_withhold": withhold,
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
def withhold(request):
    return request.param


@fixture
def otm_order_confirmation(otm_request_parameters):
    return {
        "type": "Feature",
        "geometry": {
            "bbox": [0, 0, 0, 0],
            "type": "Point",
            "coordinates": otm_request_parameters["coordinates"],
        },
        "properties": {
            "addon:withhold": otm_request_parameters["addon_withhold"],
            "product": "standard",
            "datetime": (
                f"{otm_request_parameters['date_from']}/"
                f"{otm_request_parameters['date_to']}"
            ),
            "satvu:day_night_mode": "day",
            "max_cloud_cover": otm_request_parameters["max_cloud_cover"],
            "min_off_nadir": otm_request_parameters["min_off_nadir"],
            "max_off_nadir": otm_request_parameters["min_off_nadir"],
            "min_gsd": 3.5,
            "max_gsd": 6.8,
        },
    }


@fixture
def otm_order_response(otm_request_parameters):
    return {
        "type": "Feature",
        "geometry": {"bbox": [0, 0, 0, 0], "type": "Point", "coordinates": [0, 0]},
        "properties": {
            "addon:withhold": "0d",
            "product": "standard",
            "datetime": "2023-03-22T12:50:24+01:00/2023-03-23T12:50:24+01:00",
            "satvu:day_night_mode": "day",
            "max_cloud_cover": 15,
            "min_off_nadir": 0,
            "max_off_nadir": 30,
            "min_gsd": 3.5,
            "max_gsd": 6.8,
            "status": "committed",
            "created_at": "2019-08-24T14:15:22Z",
            "updated_at": "2019-08-24T14:15:22Z",
        },
        "id": "1ed44bb9-064e-4973-b15a-c5cc460d6677",
        "links": [
            {
                "href": "http://example.com",
                "rel": "string",
                "method": "GET",
                "body": {},
                "merge": False,
                "type": "string",
                "title": "string",
            }
        ],
        "contract_id": otm_request_parameters["contract_id"],
        "price": {
            "currency": "GBP",
            "base": 100000,
            "addon:withhold": 10000,
            "total": 110000,
            "value": 110000,
        },
    }


@fixture()
def otm_feasibility_body(otm_request_parameters):
    return {
        "bbox": [0, 0, 0, 0],
        "type": "Feature",
        "geometry": {"bbox": [0, 0, 0, 0], "type": "Point", "coordinates": [0, 0]},
        "properties": {
            "product": "standard",
            "datetime": "2023-03-22T12:50:24+01:00/2023-03-23T12:50:24+01:00",
            "satvu:day_night_mode": "day",
            "max_cloud_cover": 15,
            "min_off_nadir": 0,
            "max_off_nadir": 30,
            "min_gsd": 3.5,
            "max_gsd": 6.8,
            "status": "pending",
            "created_at": "2019-08-24T14:15:22Z",
            "updated_at": "2019-08-24T14:15:22Z",
            "price": {"value": 100000, "currency": "GBP"},
        },
        "id": "1ed44bb9-064e-4973-b15a-c5cc460d6677",
        "links": [
            {
                "href": "http://example.com",
                "rel": "string",
                "method": "GET",
                "body": {},
                "merge": False,
                "type": "string",
                "title": "string",
            }
        ],
        "contract_id": otm_request_parameters["contract_id"],
    }


@fixture
def otm_feasibility_response_body(otm_request_parameters):
    return {
        "bbox": [0, 0, 0, 0],
        "type": "FeatureCollection",
        "features": [
            {
                "bbox": [0, 0, 0, 0],
                "type": "Feature",
                "geometry": {
                    "bbox": [0, 0, 0, 0],
                    "type": "Point",
                    "coordinates": [0, 0],
                },
                "properties": {
                    "product": "standard",
                    "datetime": "2023-03-22T12:50:24+01:00/2023-03-23T12:50:24+01:00",
                    "satvu:day_night_mode": "day",
                    "max_cloud_cover": 15,
                    "min_off_nadir": 0,
                    "max_off_nadir": 30,
                    "min_gsd": 3.5,
                    "max_gsd": 6.8,
                    "created_at": "2019-08-24T14:15:22Z",
                    "updated_at": "2019-08-24T14:15:22Z",
                    "price": {"value": 100000, "currency": "GBP"},
                    "min_sun_el": 0,
                    "max_sun_el": 0,
                },
                "id": "1ed44bb9-064e-4973-b15a-c5cc460d6677",
            }
        ],
        "id": "1ed44bb9-064e-4973-b15a-c5cc460d6677",
        "links": [
            {
                "href": "http://example.com",
                "rel": "string",
                "method": "GET",
                "body": {},
                "merge": False,
                "type": "string",
                "title": "string",
            }
        ],
        "status": "pending",
        "contract_id": otm_request_parameters["contract_id"],
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
                    "created_at": "2023-10-06T08:56:26Z",
                    "updated_at": "2023-10-06T08:56:28Z",
                },
                "id": "57645c80-fda4-4116-9270-6f1b2a097000",
                "contract_id": "74841d4e-60d4-4e73-a691-2dddffa10d92",
                "collection": "feasibility",
            },
        ],
        "context": {"limit": 25, "matched": 1, "returned": 1},
        "links": [],
    }


@fixture(autouse=True)
def mocketize_fixture():
    with Mocketizer():
        yield


@fixture(scope="session", autouse=True)
def _setup_pact_logging() -> None:
    """
    Set up logging for the pact package.
    """
    from pact.v3 import ffi

    ffi.log_to_stderr("INFO")


@fixture
def pact(request) -> Generator[Pact, None, None]:
    pact_dir = "./pacts"
    pact = Pact("python-sdk", request.param)
    yield pact.with_specification("V4")
    pact.write_file(pact_dir)


@fixture(autouse=True)
def allure_metadata():
    """Allure labels to be added at runtime"""
    allure.dynamic.label("layer", "unit")
    allure.dynamic.feature("Python SDK")
