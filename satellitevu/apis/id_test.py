from allure import description, story, title
import json
import re
from urllib.parse import urlparse
from uuid import uuid4

from pytest import raises, mark
from mocket import Mocket
from mocket.mockhttp import Entry

from satellitevu.apis.exceptions import IDAPIError


@mark.parametrize("pact", ["id-service"], indirect=True)
@mark.usefixtures("mocketize_fixture")
@story("ID")
class TestID:
    @title("Get user details")
    @description("Retrieve the details of a user.")
    def test_get_user_details(self, oauth_token_entry, client, pact):
        api_path = "id/v2/user/details"

        id_response_body = json.dumps(
            {
                "user_id": "string",
                "name": "string",
                "email": "string",
                "user_metadata": {
                    "client_id": "string",
                    "notifications": [
                        {
                            "category": "tasking",
                            "settings": [
                                {
                                    "topic": "tasking:order_status",
                                    "name": "string",
                                    "description": "string",
                                    "email": False,
                                }
                            ],
                        }
                    ],
                },
                "last_login": "string",
            }
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=id_response_body,
        )

        response = client.id_v2.get_user_details()

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Request for user information")
            .given("user exists")
            .with_request(method="GET", path="/user/details")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Rotate client secret")
    @description("Rotate the client secret.")
    def test_rotate_client_secret(self, oauth_token_entry, client, pact):
        api_path = "id/v2/client/reset"
        id_response_body = json.dumps(
            {
                "client_id": "client_id",
                "client_secret": "client_secret",  # pragma: allowlist secret
            }
        )

        Entry.single_register(
            "POST", client._gateway_url + api_path, status=200, body=id_response_body
        )

        response = client.id_v2.rotate_client_secret()
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Request to rotate the client secret")
            .given("a client exists")
            .with_request(method="POST", path="/client/reset")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Edit user settings")
    @description("Edit the user settings.")
    def test_edit_user_settings(self, oauth_token_entry, client, pact):
        api_path = "id/v2/user/settings"
        id_response_body = json.dumps(
            {
                "user_id": "string",
                "name": "string",
                "email": "string",
                "user_metadata": {
                    "client_id": "string",
                    "notifications": [
                        {
                            "category": "tasking",
                            "settings": [
                                {
                                    "topic": "tasking:order_status",
                                    "name": "string",
                                    "description": "string",
                                    "email": False,
                                }
                            ],
                        }
                    ],
                },
                "last_login": "string",
            }
        )
        Entry.single_register(
            "PUT", client._gateway_url + api_path, status=200, body=id_response_body
        )
        notifications = [
            {
                "category": "tasking",
                "settings": [{"email": False, "topic": "tasking:order_status"}],
            }
        ]

        response = client.id_v2.edit_user_settings(notifications)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry
        (
            pact.upon_receiving("Request to edit the user settings")
            .given("user exists")
            .with_request(method="PUT", path="/user/settings")
            .with_body(api_request.body)
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Edit user settings with invalid payload")
    @description("Edit the user settings with an invalid payload.")
    def test_edit_user_settings_invalid_notifications_payload(
        self, oauth_token_entry, client, pact
    ):
        api_path = "id/v2/user/settings"
        id_response_body = json.dumps(
            {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}
        )
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
            match=re.escape(f"ID API Error - 422 : {id_response_body}"),
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

        (
            pact.upon_receiving("Invalid request to edit the user settings")
            .given("user exists")
            .with_request(method="PUT", path="/user/settings")
            .with_body(api_request.body)
            .will_respond_with(422)
            .with_body(id_response_body)
        )

    @title("Get credit balance")
    @description("Retrieve the credit balance for a contract.")
    def test_get_credit_balance(self, oauth_token_entry, client, pact):
        contract_id = str(uuid4())
        api_path = f"id/v2/{contract_id}/wallet/credit"
        id_response_body = json.dumps(
            {
                "currency": "GBP",
                "balance": 100000,
            }
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=id_response_body,
        )

        response = client.id_v2.get_credit_balance(contract_id)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Request for the contract's balance")
            .given("contract exists")
            .with_request(method="GET", path=f"/{contract_id}/wallet/credit")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Create webhook")
    @description("Create a webhook with a given payload.")
    def test_create_webhook(self, oauth_token_entry, client, pact):
        api_path = "id/v2/webhooks/"

        name = "My Webhook"
        url = "https://my-webhook-url.com"
        id_response_body = json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "topic": "tasking:order_status",
                    }
                ],
                "name": name,
                "url": url,
                "id": str(uuid4()),
                "signing_key": "string",
            }
        )

        Entry.single_register(
            "POST", client._gateway_url + api_path, status=200, body=id_response_body
        )

        response = client.id_v2.create_webhook(name, url, ["tasking:order_status"])
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Create a webhook")
            .given("user exists")
            .with_request(method="POST", path="/webhooks")
            .with_body(api_request.body)
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Create webhook with invalid payload")
    @description("Create a webhook with an invalid payload.")
    def test_create_webhook_invalid_payload(self, oauth_token_entry, client, pact):
        api_path = "id/v2/webhooks/"

        id_response_body = json.dumps(
            {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}
        )

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            status=422,
            body=id_response_body,
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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Create a webhook invalid payload")
            .given("user exists")
            .with_request(method="POST", path="/webhooks")
            .will_respond_with(422)
            .with_body(id_response_body)
        )

    @title("Get webhook")
    @description("Retrieve the details of a webhook.")
    def test_get_webhook(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/"
        id_response_body = json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
            }
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=id_response_body,
        )

        response = client.id_v2.get_webhook(webhook_id)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Get webhook information")
            .given("webhook exists")
            .with_request(method="GET", path=f"/webhooks/{webhook_id}")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Get webhook (not found)")
    @description("Retrieve the details of a webhook that does not exist.")
    def test_get_webhook_not_found(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/"
        id_response_body = json.dumps(
            {"detail": f"Webhook with ID {webhook_id} not found."}
        )
        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=404,
            body=id_response_body,
        )

        with raises(IDAPIError):
            client.id_v2.get_webhook(webhook_id)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Webhook not found")
            .given("webhook does not exist")
            .with_request(method="GET", path=f"/webhooks/{webhook_id}")
            .will_respond_with(404)
            .with_body(id_response_body)
        )

    @title("List webhooks")
    @description("Retrieve a list of webhooks.")
    def test_list_webhooks(self, oauth_token_entry, client, pact):
        token = "token"
        api_path = f"id/v2/webhooks/?per_page=25&token={token}"
        id_response_body = json.dumps(
            {
                "webhooks": [
                    {
                        "active": True,
                        "event_types": [
                            {
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
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=id_response_body,
        )

        response = client.id_v2.list_webhooks(page_token=token)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("List webhooks")
            .given("webhooks exist")
            .with_request(method="GET", path="/webhooks")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("List webhooks (invalid token)")
    @description("Retrieve a list of webhooks with an invalid token.")
    def test_list_webhooks_invalid_token(self, oauth_token_entry, client, pact):
        token = "invalid-token"
        api_path = f"id/v2/webhooks/?per_page=25&token={token}"
        id_response_body = json.dumps(
            {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}
        )
        Entry.single_register(
            "GET", client._gateway_url + api_path, status=422, body=id_response_body
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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Get webhook with invalid token")
            .given("webhooks exist")
            .with_request(method="GET", path="/webhooks")
            .with_query_parameters({"per_page": "25", "token": token})
            .will_respond_with(422)
            .with_body(id_response_body)
        )

    @title("Edit webhook")
    @description("Edit a webhook with a given payload.")
    def test_edit_webhook(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/"

        name = "My Webhook"
        url = "https://my-webhook-url.com"
        id_response_body = json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "topic": "tasking:order_status",
                    }
                ],
                "name": name,
                "url": url,
                "id": webhook_id,
            }
        )

        Entry.single_register(
            "PATCH", client._gateway_url + api_path, status=200, body=id_response_body
        )
        response = client.id_v2.edit_webhook(webhook_id, active=False, name=name)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Edit webhook")
            .given("webhook exists")
            .with_request(method="PATCH", path=f"/webhooks/{webhook_id}")
            .with_body(api_request.body)
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Edit webhook with invalid payload")
    @description("Edit a webhook with an invalid payload.")
    def test_edit_webhook_invalid_payload(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/"
        id_response_body = json.dumps(
            {"detail": [{"loc": ["string"], "msg": "string", "type": "string"}]}
        )

        Entry.single_register(
            "PATCH",
            client._gateway_url + api_path,
            status=422,
            body=id_response_body,
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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Edit webhook with invalid payload")
            .given("webhook payload is invalid")
            .with_request(method="PATCH", path=f"/webhooks/{webhook_id}")
            .with_body(
                {
                    "active": True,
                    "event_types": ["tasking:order_status"],
                    "name": "My Webhook",
                }
            )
            .will_respond_with(422)
            .with_body(id_response_body)
        )

    @title("Delete webhook")
    @description("Delete a webhook")
    def test_delete_webhook(self, oauth_token_entry, client, pact):
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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Delete webhook")
            .given("webhook exists")
            .with_request(method="DELETE", path=f"/webhooks/{webhook_id}")
            .will_respond_with(204)
        )

    @title("Delete webhook (not found)")
    @description("Delete a webhook that does not exist.")
    def test_delete_webhook_not_found(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/"
        id_response_body = json.dumps(
            {"detail": f"Webhook with ID {webhook_id} not found."}
        )

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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Attempt to delete a nonexistent webhook")
            .given("webhook does not exist")
            .with_request(method="DELETE", path=f"/webhooks/{webhook_id}")
            .will_respond_with(404)
            .with_body(id_response_body)
        )

    @title("Rotate webhook signing key")
    @description("Rotate the webhook signing key.")
    def test_rotate_webhook_signing_key(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/rotate/"
        id_response_body = json.dumps(
            {
                "active": True,
                "event_types": [
                    {
                        "topic": "tasking:order_status",
                    }
                ],
                "name": "My Webhook",
                "url": "https://my-webhook-url.com",
                "id": webhook_id,
                "signing_key": "string",
            }
        )

        Entry.single_register(
            "POST", client._gateway_url + api_path, status=200, body=id_response_body
        )

        response = client.id_v2.rotate_webhook_signing_key(webhook_id)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Rotate webhook signing key")
            .given("webhook does not exist")
            .with_request(method="POST", path=f"/webhooks/{webhook_id}/rotate")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Rotate webhook signing key (not found)")
    @description("Rotate the signing key of a webhook that does not exist.")
    def test_rotate_webhook_signing_key_not_found(
        self, oauth_token_entry, client, pact
    ):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/rotate/"
        id_response_body = json.dumps(
            {"detail": f"Webhook with ID {webhook_id} not found."}
        )
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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Rotate webhook signing key not found")
            .given("webhook does not exist")
            .with_request(method="POST", path=f"/webhooks/{webhook_id}/rotate")
            .will_respond_with(404)
            .with_body(id_response_body)
        )

    @title("Test webhook")
    @description("Test an existing webhook.")
    def test_test_webhook(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/test/"
        id_response_body = json.dumps(
            {
                "active": True,
                "event_types": [
                    {
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
        )

        Entry.single_register(
            "POST", client._gateway_url + api_path, status=200, body=id_response_body
        )

        response = client.id_v2.test_webhook(webhook_id)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Test webhook")
            .given("webhook exists")
            .with_request(method="POST", path=f"/webhooks/{webhook_id}/test")
            .will_respond_with(200)
            .with_body(id_response_body)
        )

    @title("Test webhook (not found)")
    @description("Test a webhook that does not exist.")
    def test_test_webhook_not_found(self, oauth_token_entry, client, pact):
        webhook_id = str(uuid4())
        api_path = f"id/v2/webhooks/{webhook_id}/test/"

        id_response_body = json.dumps(
            {"detail": f"Webhook with ID {webhook_id} not found."}
        )

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
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Test webhook not found")
            .given("webhook does not exist")
            .with_request(method="POST", path=f"/webhooks/{webhook_id}/test")
            .will_respond_with(404)
            .with_body(id_response_body)
        )

    @title("Get webhook events")
    @description("Retrieve a list of webhook events.")
    def test_get_webhook_events(self, oauth_token_entry, client, pact):
        api_path = "id/v2/webhooks/events/"
        id_response_body = json.dumps(
            [
                {
                    "topic": "tasking:order_status",
                    "name": "string",
                    "description": "string",
                }
            ]
        )
        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=id_response_body,
        )

        response = client.id_v2.get_webhook_events()
        assert isinstance(response, list)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Get webhook events")
            .given("webhooks exist")
            .with_request(method="GET", path="/webhooks/events/")
            .will_respond_with(200)
            .with_body(id_response_body)
        )
