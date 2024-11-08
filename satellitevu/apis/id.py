from typing import Any, Union, Dict
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
