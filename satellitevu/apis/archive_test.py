from datetime import datetime
from json import dumps
from urllib.parse import urlparse

import pytest
from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import mark

from satellitevu.auth.exc import Api401Error, Api403Error


@mocketize(strict_mode=True)
@mark.parametrize(
    "kwargs, payload",
    (
        ({}, {"limit": 10}),
        ({"limit": 50}, {"limit": 50}),
        (
            {
                "date_from": datetime(2022, 9, 10, 0, 0, 0),
                "date_to": datetime(2022, 10, 10, 0, 0, 0),
            },
            {"limit": 10, "datetime": "2022-09-10T00:00:00/2022-10-10T00:00:00"},
        ),
        ({"bbox": [0, 0, 1, 1]}, {"bbox": [0, 0, 1, 1], "limit": 10}),
    ),
)
def test_search(client, oauth_token_entry, kwargs, payload):
    Entry.single_register(
        "POST", client._gateway_url + "archive/v1/search", "mock-stac-response"
    )

    response = client.archive_v1.search(**kwargs)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/archive/v1/search"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == dumps(payload)
    assert response.text == "mock-stac-response"


@mocketize(strict_mode=True)
@mark.parametrize(
    "kwargs, payload, status, exception",
    (
        ({}, {"limit": 10}, 401, Api401Error),
        ({"limit": 50}, {"limit": 50}, 403, Api403Error),
    ),
)
def test_unauthorized_search(
    client, oauth_token_entry, kwargs, payload, status, exception
):
    Entry.single_register(
        "POST",
        client._gateway_url + "archive/v1/search",
        "mock-stac-response",
        status=status,
    )

    with pytest.raises(exception):
        client.archive_v1.search(**kwargs)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/archive/v1/search"
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"
    assert api_request.body == dumps(payload)

    Mocket.assert_fail_if_entries_not_served()
