import tempfile
from io import BytesIO
from json import dumps
from unittest.mock import patch
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import pytest
from mocket import Mocket, mocketize
from mocket.mockhttp import Entry, Response
from pytest import mark

from satellitevu.apis.orders import bytes_to_file
from satellitevu.auth.exc import Api401Error, Api403Error

API_PATH = "orders/v2/contract-id/"


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids",
    (
        ("20221005T214049000_basic_0_TABI"),
        ("20220923T222227000_basic_0_TABI"),
    ),
)
def test_submit_single_item(client, oauth_token_entry, item_ids):
    payload = dumps({"item_id": [item_ids]})
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        body=dumps(payload),
        status=201,
    )

    response = client.orders_v2.submit(contract_id=contract_id, item_ids=item_ids)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["content-type"] == "application/json"
    assert api_request.headers["authorization"] == oauth_token_entry
    assert api_request.body == payload

    assert response.status == 201


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids",
    (
        (["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"]),
        (["20220923T222227000_basic_0_TABI"]),
    ),
)
def test_submit_multiple_items(
    client,
    oauth_token_entry,
    item_ids,
):
    payload = dumps({"item_id": item_ids})
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        body=dumps(payload),
        status=201,
    )

    response = client.orders_v2.submit(contract_id=contract_id, item_ids=item_ids)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["content-type"] == "application/json"
    assert api_request.headers["authorization"] == oauth_token_entry
    assert api_request.body == payload

    assert response.status == 201


@mocketize(strict_mode=True)
def test_item_download_url(
    client,
    oauth_token_entry,
    redirect_response,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
    )

    response = client.orders_v2.item_download_url(
        contract_id=contract_id, order_id=order_id, item_id=item_id
    )

    requests = Mocket.request_list()

    assert len(requests) == 2
    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["authorization"] == oauth_token_entry

    assert isinstance(response, dict)
    assert response["url"] == "https://image.test"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["status", "exception"],
    (
        (401, Api401Error),
        (403, Api403Error),
    ),
)
def test_no_access_to_download_if_unauthorized(
    client,
    oauth_token_entry,
    status,
    exception,
    redirect_response,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
        status=status,
    )

    with pytest.raises(exception):
        client.orders_v2.item_download_url(
            contract_id=contract_id, order_id=order_id, item_id=item_id
        )

    requests = Mocket.request_list()

    assert len(requests) == 2
    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_download_order_item(
    client,
    oauth_token_entry,
    redirect_response,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))
    download_dir = "downloads"

    Entry.register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        Response(headers={"Retry-After": "1"}, status=202),
        Response(body=dumps(redirect_response), status=200),
    )
    Entry.single_register("GET", uri=redirect_response["url"])

    with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
        mock_file_dl.return_value = f"{download_dir}/image.zip"

        response = client.orders_v2.download_item(
            contract_id=contract_id,
            order_id=order_id,
            item_id=item_id,
            destdir=download_dir,
        )

    requests = Mocket.request_list()

    assert len(requests) == 4

    api_request = requests[2]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["authorization"] == oauth_token_entry

    mock_file_dl.assert_called_once()
    assert response == mock_file_dl()
    assert isinstance(response, str)

    Mocket.assert_fail_if_entries_not_served()


@mocketize(strict_mode=True)
def test_get_order_details(
    client,
    oauth_token_entry,
    order_details_response,
):
    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps(order_details_response),
    )

    response = client.orders_v2.get_order_details(
        contract_id=contract_id, order_id=fake_uuid
    )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["authorization"] == oauth_token_entry

    assert isinstance(response, dict)


@mocketize(strict_mode=True)
def test_get_orders(
    client,
    oauth_token_entry,
    order_details_response,
):
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        body=dumps(order_details_response),
    )

    response = client.orders_v2.get_orders(contract_id=contract_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["authorization"] == oauth_token_entry

    assert isinstance(response, dict)


@mocketize(strict_mode=True)
@mark.parametrize(
    ["status", "exception"],
    (
        (401, Api401Error),
        (403, Api403Error),
    ),
)
def test_cannot_get_order_details_if_unauthorized(
    client,
    oauth_token_entry,
    status,
    exception,
    order_details_response,
):
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps(order_details_response),
        status=status,
    )

    with pytest.raises(exception):
        client.orders_v2.get_order_details(contract_id=contract_id, order_id=fake_uuid)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_download_order(
    client,
    oauth_token_entry,
    redirect_response,
):
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))
    order_id = "528b0f77-5df1-4ed7-9224-502817170613"
    download_dir = "downloads"

    Entry.register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/download?redirect=False",
        Response(headers={"Retry-After": "1"}, status=202),
        Response(body=dumps(redirect_response), status=200),
    )
    Entry.single_register("GET", uri=redirect_response["url"])

    with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
        mock_file_dl.return_value = f"{download_dir}/{order_id}.zip"

        response = client.orders_v2.download_order(
            contract_id=contract_id, order_id=order_id, destdir=download_dir
        )

    requests = Mocket.request_list()

    assert len(requests) == 4

    api_request = requests[1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{order_id}/download?redirect=False"
    assert api_request.headers["authorization"] == oauth_token_entry

    mock_file_dl.assert_called_once()
    assert response == mock_file_dl()
    assert isinstance(response, str)

    Mocket.assert_fail_if_entries_not_served()


@mocketize(strict_mode=True)
@mark.parametrize(
    ["status", "exception"],
    (
        (401, Api401Error),
        (403, Api403Error),
    ),
)
def test_download_order_unauthorized(
    client,
    redirect_response,
    status,
    exception,
):
    contract_id = str(uuid4())
    api_path = API_PATH.replace("contract-id", str(contract_id))

    order_id = "528b0f77-5df1-4ed7-9224-502817170613"
    download_dir = "downloads"

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": None}),
    )

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/download?redirect=False",
        body=dumps(redirect_response),
        status=status,
    )

    with pytest.raises(exception):
        client.orders_v2.download_order(
            contract_id=contract_id, order_id=order_id, destdir=download_dir
        )

    requests = Mocket.request_list()

    assert len(requests) == 2

    api_request = requests[1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{order_id}/download?redirect=False"
    assert api_request.headers["authorization"] == "Bearer None"


def test_bytes_to_file():
    outfile_path = tempfile.mkstemp()[1]
    output = bytes_to_file(BytesIO(b"Hello world"), outfile_path)

    assert isinstance(output, str)
