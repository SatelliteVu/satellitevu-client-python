from json import dumps
from urllib.parse import urljoin, urlparse

from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import mark

from satellitevu.client import Client


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids",
    (
        "20220211T031818000_L1C_30_EM",
        "20220923T222227000_basic_0_TABI",
    ),
)
def test_submit_single_items(memory_cache, item_ids):
    client = Client(
        client_id="mock-id", client_secret="mock-secret", cache=memory_cache
    )

    payload = dumps({"item_id": [item_ids]})

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "mock-token"}),
    )

    Entry.single_register("POST", client._gateway_url + "orders/v1/", body=payload)

    response = client.orders_v1.submit(item_ids)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/orders/v1/"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == payload

    assert response.status == 200


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids",
    (
        ["20220211T031818000_L1C_30_EM", "20220923T222227000_basic_0_TABI"],
        ["20220923T222227000_basic_0_TABI"],
    ),
)
def test_submit_multiple_items(memory_cache, item_ids):
    client = Client(
        client_id="mock-id", client_secret="mock-secret", cache=memory_cache
    )

    payload = dumps({"item_id": item_ids})

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "mock-token"}),
    )

    Entry.single_register("POST", client._gateway_url + "orders/v1/", body=payload)

    response = client.orders_v1.submit(item_ids)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/orders/v1/"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == payload

    assert response.status == 200
