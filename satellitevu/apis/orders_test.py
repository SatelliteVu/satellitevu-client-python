import tempfile
from io import BytesIO
from json import dumps
from unittest.mock import patch
from urllib.parse import urljoin, urlparse

from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import mark

from satellitevu.apis.orders import bytes_to_file
from satellitevu.client import Client


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids",
    (
        "20221005T214049000_basic_0_TABI",
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
        ["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"],
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


@mocketize(strict_mode=True)
def test_item_download_url(memory_cache, redirect_response):
    order_id = "uuid"
    item_id = "image"

    client = Client(
        client_id="mock-id", client_secret="mock-secret", cache=memory_cache
    )

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "mock-token"}),
    )

    Entry.single_register(
        "GET",
        client._gateway_url + f"orders/v1/{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
    )

    response = client.orders_v1.item_download_url(order_id, item_id)
    requests = Mocket.request_list()

    assert len(requests) == 2
    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/orders/v1/uuid/image/download?redirect=False"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    assert isinstance(response, dict)
    assert response["url"] == "https://image.test"


@mocketize(strict_mode=True)
def test_download_order_item(memory_cache, redirect_response):
    order_id = "uuid"
    item_id = "image"

    client = Client(
        client_id="mock-id", client_secret="mock-secret", cache=memory_cache
    )

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "mock-token"}),
    )

    Entry.single_register(
        "GET",
        client._gateway_url + f"orders/v1/{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
    )

    Entry.single_register("GET", uri="https://image.test")

    requests = Mocket.request_list()

    with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
        mock_file_dl.return_value = "Downloads/image.zip"
        client.orders_v1.download_item(order_id, item_id)

    assert len(requests) == 3

    api_request = requests[1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/orders/v1/uuid/image/download?redirect=False"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    mock_file_dl.assert_called_once()

    Mocket.assert_fail_if_entries_not_served()


def test_bytes_to_file():
    outfile_path = tempfile.mkstemp()[1]
    output = bytes_to_file(BytesIO(b"Hello world"), outfile_path)

    assert isinstance(output, str)
