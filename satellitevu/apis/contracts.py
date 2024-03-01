from typing import Union
from uuid import UUID

from satellitevu.auth import Auth
from satellitevu.http import AbstractClient

from .base import AbstractApi
from .exceptions import ContractAccessError


class ContractsV1(AbstractApi):
    """
    Interface for information about the contracts and associated products a
    customer has access to.
    """

    api_path = "policy/v1"

    def __init__(self, client: AbstractClient, base_url: str, auth: Auth):
        super().__init__(client, base_url)
        self._auth = auth

    def get_contracts(self):
        url = self.url("/contracts")
        response = self.make_request(
            method="POST",
            url=url,
            json={"token": self._auth.token()},
        )

        if response.status != 200:
            raise ContractAccessError(response.status, response.text)

        return response.json()["result"]

    def get_contract_pricebook(self, contract_id: Union[UUID, str]):
        url = self.url("/policy/query/products")
        response = self.make_request(
            method="POST",
            url=url,
            json={"token": self._auth.token(), "contract_id": str(contract_id)},
        )

        if response.status != 200:
            raise ContractAccessError(response.status, response.text)

        return response.json()["result"]
