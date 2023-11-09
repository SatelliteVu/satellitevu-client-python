from datetime import datetime
from json import dumps
from urllib.parse import urlparse
from uuid import uuid4

import pytest
from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import fixture, mark

from satellitevu.auth.exc import Api401Error, Api403Error


@fixture()
def versioned_archive_client(request, client):
    if request.getfixturevalue("version") == "v1":
        yield client.archive_v1
    else:
        yield client.archive_v2


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_archive_client", "kwargs", "payload"],
    (
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {},
            {"limit": 10},
        ),
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {"limit": 50},
            {"limit": 50},
        ),
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {
                "date_from": datetime(2022, 9, 10, 0, 0, 0),
                "date_to": datetime(2022, 10, 10, 0, 0, 0),
            },
            {"limit": 10, "datetime": "2022-09-10T00:00:00/2022-10-10T00:00:00"},
        ),
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {"bbox": [0, 0, 1, 1]},
            {"bbox": [0, 0, 1, 1], "limit": 10},
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {},
            {"limit": 10},
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {"limit": 50},
            {"limit": 50},
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {
                "date_from": datetime(2022, 9, 10, 0, 0, 0),
                "date_to": datetime(2022, 10, 10, 0, 0, 0),
            },
            {"limit": 10, "datetime": "2022-09-10T00:00:00/2022-10-10T00:00:00"},
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {"bbox": [0, 0, 1, 1]},
            {"bbox": [0, 0, 1, 1], "limit": 10},
        ),
    ),
    indirect=["versioned_archive_client"],
)
def test_search(
    client,
    oauth_token_entry,
    version,
    api_path,
    versioned_archive_client,
    kwargs,
    payload,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST", client._gateway_url + f"{api_path}search", "mock-stac-response"
    )

    if version == "v1":
        assert contract_id not in versioned_archive_client.api_path
        response = versioned_archive_client.search(**kwargs)
    else:
        response = versioned_archive_client.search(contract_id=contract_id, **kwargs)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}search"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == dumps(payload)
    assert response.text == "mock-stac-response"


@mocketize(strict_mode=True)
@mark.parametrize(
    "version, api_path, versioned_archive_client, kwargs, payload, status, exception",
    (
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {},
            {"limit": 10},
            401,
            Api401Error,
        ),
        (
            "v1",
            "archive/v1/",
            "versioned_archive_client",
            {"limit": 50},
            {"limit": 50},
            403,
            Api403Error,
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {},
            {"limit": 10},
            401,
            Api401Error,
        ),
        (
            "v2",
            "archive/v2/contract-id/",
            "versioned_archive_client",
            {"limit": 50},
            {"limit": 50},
            403,
            Api403Error,
        ),
    ),
    indirect=["versioned_archive_client"],
)
def test_unauthorized_search(
    client,
    oauth_token_entry,
    version,
    api_path,
    versioned_archive_client,
    kwargs,
    payload,
    status,
    exception,
):
    contract_id = str(uuid4())
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + f"{api_path}search",
        "mock-stac-response",
        status=status,
    )

    with pytest.raises(exception):
        if version == "v1":
            versioned_archive_client.search(**kwargs)
        else:
            versioned_archive_client.search(contract_id=contract_id, **kwargs)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == f"/{api_path}search"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == dumps(payload)

    Mocket.assert_fail_if_entries_not_served()
