from typing import Any, Union, Dict, List, Optional
from uuid import UUID

from satellitevu.apis.base import AbstractApi
from satellitevu.apis.exceptions import IDAPIError


class IdV2(AbstractApi):
    """
    Client interface to the ID API located at
    https://api.satellitevu.com/id/v2/docs
    """

    api_path = "id/v2"

    def get_user_details(self):
        """
        Retrieves the details of a user.

        Returns:
            A dictionary containing properties of the user.
        """
        url = self.url("user/details")
        response = self.make_request(method="GET", url=url)
        return response.json()

    def rotate_client_secret(self):
        """
        Generate a new client secret for the M2M client associated with a user.

        Returns:
            A dictionary containing the client ID and new secret of the user.
        """
        url = self.url("client/reset")
        response = self.make_request(method="POST", url=url)
        return response.json()

    def edit_user_settings(self, notifications: Dict[str, Any]):
        """
        Update user settings.
        """
        url = self.url("user/settings")
        response = self.make_request(
            method="PUT", url=url, json={"notifications": notifications}
        )
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def get_credit_balance(self, contract_id: Union[UUID, str]):
        """
        Retrieves the credit balance. This is calculated as the credit limit
        for the contract minus the total credits used.
        """
        url = self.url(f"{str(contract_id)}/wallet/credit")
        response = self.make_request(method="GET", url=url)
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def create_webhook(
        self,
        name: str,
        url: str,
        event_types: List[str],
        **kwargs,
    ):
        """
        Create a webhook.

        Args:
            name: The name of the webhook.

            url: The URL where you want to receive requests for events you are subscribed to.
            Must be HTTPS.

            event_types: A list of events to subscribe to.

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            A dictionary containing properties of the created webhook.
        """
        payload = {
            "event_types": event_types,
            "name": name,
            "url": url,
            **kwargs,
        }

        response = self.make_request(
            method="POST",
            url=self.url("webhooks/"),
            json=payload,
        )

        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def get_webhook(self, webhook_id: Union[UUID, str]):
        """
        Get information about an existing webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            A dictionary containing properties of the webhook.
        """
        response = self.make_request(
            method="GET",
            url=self.url(f"webhooks/{str(webhook_id)}/"),
        )
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def list_webhooks(
        self,
        per_page: int = 25,
        page_token: Optional[str] = None,
    ):
        """
        List all webhooks.

        Args:
            per_page: Number of results (defaults to 25) to be returned per page.

            page_token: Optional string key used to return specific page of results.
            Defaults to None -> assumes page 0.

        Returns:
            A list of dictionaries containing properties of each webhook.
        """

        url = self.url(f"webhooks/?per_page={per_page}")
        if page_token:
            url += f"&token={page_token}"

        response = self.make_request(method="GET", url=url)
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def edit_webhook(
        self,
        webhook_id: Union[UUID, str],
        active: Optional[bool] = None,
        event_types: Optional[List[str]] = None,
        name: Optional[str] = None,
        **kwargs,
    ):
        """
        Edit a webhook.

        Args:
            webhook_id: The webhook ID.

            active: Whether the webhook should be active or not.

            event_types: A list of events to subscribe to.

            name: The name of the webhook.

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            A dictionary containing properties of the webhook.
        """
        payload = {**kwargs}

        if active:
            payload["active"] = active
        if event_types:
            payload["event_types"] = event_types
        if name:
            payload["name"] = name

        response = self.make_request(
            method="PATCH",
            url=self.url(f"webhooks/{webhook_id}/"),
            json=payload,
        )
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def delete_webhook(self, webhook_id: Union[UUID, str]):
        """
        Delete a webhook.

        Args:
            webhook_id: The webhook ID.
        """

        response = self.make_request(
            method="DELETE",
            url=self.url(
                f"webhooks/{webhook_id}/",
            ),
        )
        if response.status != 204:
            raise IDAPIError(response.status, response.text)

    def rotate_webhook_signing_key(self, webhook_id: Union[UUID, str]):
        """
        Rotate the signing key for a webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            A dictionary containing properties of the webhook,
            including the new signing key.
        """
        response = self.make_request(
            method="POST", url=self.url(f"webhooks/{webhook_id}/rotate/")
        )
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def test_webhook(self, webhook_id: Union[UUID, str]):
        """
        Test a webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            A dictionary containing properties of the webhook
            and details about the result of the test.
        """
        response = self.make_request(
            method="POST", url=self.url(f"/webhooks/{webhook_id}/test/")
        )
        if response.status != 200:
            raise IDAPIError(response.status, response.text)
        return response.json()

    def get_webhook_events(self):
        """
        Retrieves all webhook event types.

        Returns:
            A list of all webhook event types.
        """
        response = self.make_request(method="GET", url=self.url("webhooks/events/"))
        return response.json()
