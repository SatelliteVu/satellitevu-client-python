import tempfile
from io import BytesIO
from json import dumps
from unittest.mock import patch
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import pytest
from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import fixture, mark

from satellitevu.apis.orders import bytes_to_file
from satellitevu.auth.exc import Api401Error, Api403Error


@fixture()
def versioned_orders_client(request, client):
    if request.getfixturevalue("version") == "v1":
        yield client.orders_v1
    else:
        yield client.orders_v2


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client", "item_ids"],
    (
        (
            "v1",
            "orders/v1/",
            "versioned_orders_client",
            "20221005T214049000_basic_0_TABI",
        ),
        (
            "v1",
            "orders/v1/",
            "versioned_orders_client",
            "20220923T222227000_basic_0_TABI",
        ),
        (
            "v2",
            "orders/v2/contract-id/",
            "versioned_orders_client",
            "20221005T214049000_basic_0_TABI",
        ),
        (
            "v2",
            "orders/v2/contract-id/",
            "versioned_orders_client",
            "20220923T222227000_basic_0_TABI",
        ),
    ),
    indirect=["versioned_orders_client"],
)
def test_submit_single_item(
    client, oauth_token_entry, item_ids, version, versioned_orders_client, api_path
):
    payload = dumps({"item_id": [item_ids]})
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        body=dumps(payload),
        status=201,
    )

    if version == "v1":
        assert contract_id not in versioned_orders_client.api_path
        response = versioned_orders_client.submit(item_ids)
    else:
        response = versioned_orders_client.submit(
            contract_id=contract_id, item_ids=item_ids
        )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == payload

    assert response.status == 201


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client", "item_ids"],
    (
        (
            "v1",
            "orders/v1/",
            "versioned_orders_client",
            ["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"],
        ),
        (
            "v1",
            "orders/v1/",
            "versioned_orders_client",
            ["20220923T222227000_basic_0_TABI"],
        ),
        (
            "v2",
            "orders/v2/contract-id/",
            "versioned_orders_client",
            ["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"],
        ),
        (
            "v2",
            "orders/v2/contract-id/",
            "versioned_orders_client",
            ["20220923T222227000_basic_0_TABI"],
        ),
    ),
    indirect=["versioned_orders_client"],
)
def test_submit_multiple_items(
    client,
    oauth_token_entry,
    item_ids,
    version,
    versioned_orders_client,
    api_path,
):
    payload = dumps({"item_id": item_ids})
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        body=dumps(payload),
        status=201,
    )

    if version == "v1":
        assert contract_id not in versioned_orders_client.api_path
        response = versioned_orders_client.submit(item_ids)
    else:
        response = versioned_orders_client.submit(
            contract_id=contract_id, item_ids=item_ids
        )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == payload

    assert response.status == 201


@mocketize(strict_mode=True)
@mark.parametrize(
    "item_ids, status, exception",
    (
        ("20221005T214049000_basic_0_TABI", 401, Api401Error),
        (
            ["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"],
            403,
            Api403Error,
        ),
    ),
)
def test_cannot_submit_unauthorized_order_v1(
    client, oauth_token_entry, item_ids, status, exception
):
    if isinstance(item_ids, str):
        item_ids = [item_ids]
    payload = dumps({"item_id": item_ids})

    Entry.single_register(
        "POST", client._gateway_url + "orders/v1/", body=payload, status=status
    )

    with pytest.raises(exception):
        client.orders_v1.submit(item_ids)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/orders/v1/"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == payload


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client"],
    (
        ("v1", "orders/v1/", "versioned_orders_client"),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client"),
    ),
    indirect=["versioned_orders_client"],
)
def test_item_download_url(
    client,
    oauth_token_entry,
    version,
    api_path,
    versioned_orders_client,
    redirect_response,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
    )

    if version == "v1":
        assert contract_id not in versioned_orders_client.api_path
        response = versioned_orders_client.item_download_url(order_id, item_id)
    else:
        response = versioned_orders_client.item_download_url(
            contract_id=contract_id, order_id=order_id, item_id=item_id
        )

    requests = Mocket.request_list()

    assert len(requests) == 2
    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    assert isinstance(response, dict)
    assert response["url"] == "https://image.test"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client", "status", "exception"],
    (
        ("v1", "orders/v1/", "versioned_orders_client", 401, Api401Error),
        ("v1", "orders/v1/", "versioned_orders_client", 403, Api403Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 401, Api401Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 403, Api403Error),
    ),
    indirect=["versioned_orders_client"],
)
def test_no_access_to_download_if_unauthorized(
    client,
    oauth_token_entry,
    status,
    exception,
    redirect_response,
    version,
    api_path,
    versioned_orders_client,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
        status=status,
    )

    with pytest.raises(exception):
        if version == "v1":
            versioned_orders_client.item_download_url(order_id, item_id)
        else:
            versioned_orders_client.item_download_url(
                contract_id=contract_id, order_id=order_id, item_id=item_id
            )

    requests = Mocket.request_list()

    assert len(requests) == 2
    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["Authorization"] == "Bearer mock-token"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client"],
    (
        ("v1", "orders/v1/", "versioned_orders_client"),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client"),
    ),
    indirect=["versioned_orders_client"],
)
def test_download_order_item(
    client,
    oauth_token_entry,
    redirect_response,
    version,
    api_path,
    versioned_orders_client,
):
    order_id = "uuid"
    item_id = "image"
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{order_id}/{item_id}/download?redirect=False",
        body=dumps(redirect_response),
    )
    Entry.single_register("GET", uri="https://image.test")

    requests = Mocket.request_list()

    with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
        mock_file_dl.return_value = "Downloads/image.zip"

        if version == "v1":
            assert contract_id not in versioned_orders_client.api_path
            response = versioned_orders_client.download_item(
                order_id, item_id, "Downloads"
            )
        else:
            response = versioned_orders_client.download_item(
                contract_id=contract_id,
                order_id=order_id,
                item_id=item_id,
                destdir="Downloads",
            )

    assert len(requests) == 3

    api_request = requests[1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}uuid/image/download?redirect=False"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    mock_file_dl.assert_called_once()
    assert response == mock_file_dl()

    Mocket.assert_fail_if_entries_not_served()


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client"],
    (
        ("v1", "orders/v1/", "versioned_orders_client"),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client"),
    ),
    indirect=["versioned_orders_client"],
)
def test_get_order_details(
    client,
    oauth_token_entry,
    order_details_response,
    version,
    api_path,
    versioned_orders_client,
):
    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps(order_details_response),
    )

    if version == "v1":
        assert contract_id not in versioned_orders_client.api_path
        response = versioned_orders_client.get_order_details(fake_uuid)
    else:
        response = versioned_orders_client.get_order_details(
            contract_id=contract_id, order_id=fake_uuid
        )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    assert isinstance(response, dict)


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client"],
    (
        ("v1", "orders/v1/", "versioned_orders_client"),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client"),
    ),
    indirect=["versioned_orders_client"],
)
def test_get_orders(
    client,
    oauth_token_entry,
    order_details_response,
    version,
    api_path,
    versioned_orders_client,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        body=dumps(order_details_response),
    )

    if version == "v1":
        assert contract_id not in versioned_orders_client.api_path
        response = versioned_orders_client.get_orders()
    else:
        response = versioned_orders_client.get_orders(contract_id=contract_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    assert isinstance(response, dict)


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client", "status", "exception"],
    (
        ("v1", "orders/v1/", "versioned_orders_client", 401, Api401Error),
        ("v1", "orders/v1/", "versioned_orders_client", 403, Api403Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 401, Api401Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 403, Api403Error),
    ),
    indirect=["versioned_orders_client"],
)
def test_cannot_get_order_details_if_unauthorized(
    client,
    oauth_token_entry,
    status,
    exception,
    order_details_response,
    version,
    api_path,
    versioned_orders_client,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps(order_details_response),
        status=status,
    )

    with pytest.raises(exception):
        if version == "v1":
            versioned_orders_client.get_order_details(fake_uuid)
        else:
            versioned_orders_client.get_order_details(
                contract_id=contract_id, order_id=fake_uuid
            )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["Authorization"] == "Bearer mock-token"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client"],
    (
        ("v1", "orders/v1/", "versioned_orders_client"),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client"),
    ),
    indirect=["versioned_orders_client"],
)
def test_download_order(
    client,
    order_details_response,
    redirect_response,
    version,
    api_path,
    versioned_orders_client,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))
    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"
    download_dir = "downloads"

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": None}),
    )

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps({**order_details_response, **{"access_token": None}}),
    )

    with patch(
        "satellitevu.apis.orders.OrdersV1._save_order_to_zip"
    ) as mock_zip_v1, patch(
        "satellitevu.apis.orders.OrdersV2._save_order_to_zip"
    ) as mock_zip_v2:
        mock_zip_v1.return_value = f"{download_dir}/SatelliteVu_{fake_uuid}.zip"
        mock_zip_v2.return_value = f"{download_dir}/SatelliteVu_{fake_uuid}.zip"

        if version == "v1":
            assert contract_id not in versioned_orders_client.api_path
            response = versioned_orders_client.download_order(fake_uuid, download_dir)

        else:
            response = versioned_orders_client.download_order(
                contract_id=contract_id, order_id=fake_uuid, destdir=download_dir
            )

    requests = Mocket.request_list()

    assert len(requests) == 2

    api_request = requests[1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["Authorization"] == "Bearer None"

    if version == "v1":
        mock_zip_v1.assert_called_once()
        assert response == mock_zip_v1()
    else:
        mock_zip_v2.assert_called_once()
        assert response == mock_zip_v2()

    assert isinstance(response, str)

    Mocket.assert_fail_if_entries_not_served()


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_orders_client", "status", "exception"],
    (
        ("v1", "orders/v1/", "versioned_orders_client", 401, Api401Error),
        ("v1", "orders/v1/", "versioned_orders_client", 403, Api403Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 401, Api401Error),
        ("v2", "orders/v2/contract-id/", "versioned_orders_client", 403, Api403Error),
    ),
    indirect=["versioned_orders_client"],
)
def test_download_order_unauthorized(
    client,
    order_details_response,
    redirect_response,
    status,
    exception,
    version,
    api_path,
    versioned_orders_client,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    fake_uuid = "528b0f77-5df1-4ed7-9224-502817170613"
    download_dir = "downloads"

    Entry.single_register(
        "POST",
        urljoin(client.auth.auth_url, "oauth/token"),
        body=dumps({"access_token": None}),
    )

    Entry.single_register(
        "GET",
        client._gateway_url + f"{api_path}{fake_uuid}",
        body=dumps({**order_details_response, **{"access_token": None}}),
        status=status,
    )

    with pytest.raises(exception):
        if version == "v1":
            versioned_orders_client.download_order(fake_uuid, download_dir)
        else:
            versioned_orders_client.download_order(
                contract_id=contract_id, order_id=fake_uuid, destdir=download_dir
            )

    requests = Mocket.request_list()

    assert len(requests) == 2

    api_request = requests[1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}{fake_uuid}"
    assert api_request.headers["Authorization"] == "Bearer None"


def test_bytes_to_file():
    outfile_path = tempfile.mkstemp()[1]
    output = bytes_to_file(BytesIO(b"Hello world"), outfile_path)

    assert isinstance(output, str)
