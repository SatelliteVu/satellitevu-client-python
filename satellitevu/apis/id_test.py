import json
import re
from urllib.parse import urlparse
from uuid import uuid4

from pytest import raises
from mocket import Mocket, mocketize
from mocket.mockhttp import Entry

from satellitevu.apis.exceptions import IDAPIError


@mocketize(strict_mode=True)
def test_get_user_details(oauth_token_entry, client):
    api_path = "id/v2/user/details"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "user_id": "string",
                "name": "string",
                "email": "string",
                "user_metadata": {},
                "last_login": "string",
            }
        ),
    )

    response = client.id_v2.get_user_details()
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_rotate_client_secret(oauth_token_entry, client):
    api_path = "id/v2/client/reset"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "client_id": "client_id",
                "client_secret": "client_secret",  # pragma: allowlist secret
            }
        ),
    )

    response = client.id_v2.rotate_client_secret()
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_edit_user_settings(oauth_token_entry, client):
    api_path = "id/v2/user/settings"

    Entry.single_register(
        "PUT",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {"notifications": {"tasking": {"order_status": {"email": True}}}}
        ),
    )

    response = client.id_v2.edit_user_settings(
        {"tasking": {"order_status": {"email": True}}}
    )
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["content-type"] == "application/json"
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_edit_user_settings_invalid_notifications_payload(oauth_token_entry, client):
    api_path = "id/v2/user/settings"

    Entry.single_register(
        "PUT",
        client._gateway_url + api_path,
        status=422,
        body=json.dumps(
            {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}
        ),
    )

    with raises(
        IDAPIError,
        match=re.escape(
            'ID API Error - 422 : {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}'
        ),
    ):
        client.id_v2.edit_user_settings(
            {"tasking": {"order_status": {"email": "wrong"}}}
        )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["content-type"] == "application/json"
    assert api_request.headers["authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_get_credit_balance(oauth_token_entry, client):
    contract_id = str(uuid4())
    api_path = f"id/v2/{contract_id}/wallet/credit"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "currency": "GBP",
                "balance": "100000",
            }
        ),
    )

    response = client.id_v2.get_credit_balance(contract_id)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["authorization"] == oauth_token_entry
