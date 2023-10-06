from .base import AbstractApi


class ContractsV1(AbstractApi):
    """
    Interface to accessing the contracts and products which a customer has access to.
    """

    api_path = "policy/v1"

    def get_contracts(self):
        url = self.url("/contracts")
        response = self.make_request(
            method="POST",
            url=url,
            json={"token": self.client.h},
        )

        if response.status != 200:
            raise Exception(f"Error - {response.status} : {response.text}")

        return response.json()
