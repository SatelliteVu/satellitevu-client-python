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
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


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
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


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
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


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
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


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
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_create_webhook(oauth_token_entry, client):
    api_path = "id/v2/webhooks/"

    name = "My Webhook"
    url = "https://my-webhook-url.com"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": name,
                "url": url,
                "id": str(uuid4()),
                "signing_key": "string",
            }
        ),
    )

    response = client.id_v2.create_webhook(name, url, ["tasking:order_status"])
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_create_webhook_invalid_payload(oauth_token_entry, client):
    api_path = "id/v2/webhooks/"

    Entry.single_register(
        "POST",
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
        client.id_v2.create_webhook(
            "My Webhook", "https://my-webhook-url.com", ["tasking:order_status"]
        )

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_get_webhook(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
            }
        ),
    )

    response = client.id_v2.get_webhook(webhook_id)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_get_webhook_not_found(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=404,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
            }
        ),
    )

    with raises(IDAPIError):
        client.id_v2.get_webhook(webhook_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_list_webhooks(oauth_token_entry, client):
    token = "token"
    api_path = f"id/v2/webhooks/?per_page=25&token={token}"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "webhooks": [
                    {
                        "active": True,
                        "event_types": [
                            {
                                "description": "Receive notifications for all tasking order updates",
                                "name": "Tasking order status updates",
                                "topic": "tasking:order_status",
                            }
                        ],
                        "name": "My Webhook",
                        "url": "https://my-webhook-url.com",
                        "id": "532fcb53-4d79-4c4e-98b7-4c1a92290b06",
                    }
                ],
                "context": {"per_page": 25, "matched": 10, "returned": 10},
                "links": [{"href": "http://example.com", "rel": "next"}],
            }
        ),
    )

    response = client.id_v2.list_webhooks(page_token=token)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_list_webhooks_invalid_token(oauth_token_entry, client):
    token = "invalid-token"
    api_path = f"id/v2/webhooks/?per_page=25&token={token}"

    Entry.single_register(
        "GET",
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
        client.id_v2.list_webhooks(page_token=token)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_edit_webhook(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    name = "My Webhook"
    url = "https://my-webhook-url.com"

    Entry.single_register(
        "PATCH",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": name,
                "url": url,
                "id": webhook_id,
            }
        ),
    )

    response = client.id_v2.edit_webhook(webhook_id, active=False, name=name)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_edit_webhook_invalid_payload(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    Entry.single_register(
        "PATCH",
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
        client.id_v2.edit_webhook(webhook_id, active=False, event_types=["unknown"])

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_delete_webhook(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    Entry.single_register(
        "DELETE",
        client._gateway_url + api_path,
        status=204,
    )

    response = client.id_v2.delete_webhook(webhook_id)
    assert not response

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_delete_webhook_not_found(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/"

    Entry.single_register(
        "DELETE",
        client._gateway_url + api_path,
        status=404,
    )

    with raises(IDAPIError):
        client.id_v2.delete_webhook(webhook_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_rotate_webhook_signing_key(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/rotate/"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
                "signing_key": "string",
            }
        ),
    )

    response = client.id_v2.rotate_webhook_signing_key(webhook_id)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_rotate_webhook_signing_key_not_found(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/rotate/"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=404,
    )

    with raises(IDAPIError):
        client.id_v2.rotate_webhook_signing_key(webhook_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_test_webhook(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/test/"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "description": "Receive notifications for all tasking order updates",
                        "name": "Tasking order status updates",
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
                "webhook_result": {
                    "success": True,
                    "status_code": 200,
                    "detail": "string",
                },
            }
        ),
    )

    response = client.id_v2.test_webhook(webhook_id)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_test_webhook_not_found(oauth_token_entry, client):
    webhook_id = str(uuid4())
    api_path = f"id/v2/webhooks/{webhook_id}/test/"

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        status=404,
    )

    with raises(IDAPIError):
        client.id_v2.test_webhook(webhook_id)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry


@mocketize(strict_mode=True)
def test_get_webhook_events(oauth_token_entry, client):
    api_path = "id/v2/webhooks/events/"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=json.dumps(
            [{"topic": "string", "name": "string", "description": "string"}]
        ),
    )

    response = client.id_v2.get_webhook_events()
    assert isinstance(response, list)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == oauth_token_entry
