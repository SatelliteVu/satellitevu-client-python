import os
from time import sleep
from typing import Dict, List, Union
from uuid import UUID


from .base import AbstractApi
from .exceptions import OrdersAPIError
from .helpers import raw_response_to_bytes, bytes_to_file


class OrdersV2(AbstractApi):
    """
    Client interface to the Orders API located at
    https://api.satellitevu.com/orders/v2/docs.
    """

    api_path = "orders/v2"
    scopes = []

    def get_orders(self, *, contract_id: Union[UUID, str]) -> Dict:
        """
         Retrieve details of all imagery orders.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an order is associated with.

        Returns:
            A dictionary containing properties of the order.
        """
        url = self.url(f"/{contract_id}/")
        response = self.make_request(method="GET", url=url)

        if response.status != 200:
            raise OrdersAPIError(response.status, response.text)

        return response.json()

    def get_order_details(
        self, *, contract_id: Union[UUID, str], order_id: Union[UUID, str]
    ) -> Dict:
        """
        Retrieve details of an imagery order.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the order.
        """
        url = self.url(f"/{contract_id}/{order_id}")
        response = self.make_request(method="GET", url=url)

        if response.status != 200:
            raise OrdersAPIError(response.status, response.text)

        return response.json()

    def submit(self, *, contract_id: Union[UUID, str], item_ids: Union[List[str], str]):
        """
        Submit an imagery order for items present in the SatVu catalog.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            under which an order will be created.

            item_ids: A string or list of strings representing the image
            identifiers. For example: "20221005T214049000_basic_0_TABI" or
            ["20221005T214049000_basic_0_TABI, "20221010T222611000_basic_0_TABI"].

        Returns:
            A dictionary containing keys: id, type, features where the id field
            corresponds to an order id and features map to an array of imagery
            items described with conformity to the STAC specification.

        """
        url = self.url(f"/{contract_id}/")

        if isinstance(item_ids, str):
            item_ids = [item_ids]

        return self.make_request(method="POST", url=url, json={"item_id": item_ids})

    def _download_request(
        self,
        url: str,
        retry_factor: float,
    ):
        """
        Request download, handling retries.
        """
        while True:
            response = self.make_request(method="GET", url=url)

            if response.status == 202:
                sleep(retry_factor * int(response.headers["Retry-After"]))
            elif response.status == 200:
                break

        return response.json()

    def item_download_url(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: Union[UUID, str],
        item_id: str,
        retry_factor: float = 1.0,
    ) -> Dict:
        """
        Finds the download url for an item in a submitted imagery order.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an item in the order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            item_id: A string representing the specific image identifiers e.g.
            "20221010T222611000_basic_0_TABI".

            retry_factor: A float that determines how retries will be handled.
            A factor of 0.5 means that only half the time specified by the
            "Retry-After" header will be observed before the download request
            is retried again. Defaults to 1.0.

        Returns:
            A dictionary containing the url which the image can be downloaded from.
        """
        url = self.url(f"/{contract_id}/{order_id}/{item_id}/download?redirect=False")

        return self._download_request(url, retry_factor=retry_factor)

    def order_download_url(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: Union[UUID, str],
        retry_factor: float = 1.0,
    ) -> Dict:
        """
        Finds the download url for a submitted imagery order.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which the order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            retry_factor: A float that determines how retries will be handled.
            A factor of 0.5 means that only half the time specified by the
            "Retry-After" header will be observed before the download request
            is retried again. Defaults to 1.0.

        Returns:
            A dictionary containing the url which the image can be downloaded from.
        """
        url = self.url(f"/{contract_id}/{order_id}/download?redirect=False")

        return self._download_request(url, retry_factor=retry_factor)

    def download_item(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: UUID,
        item_id: str,
        destdir: str,
        retry_factor: float = 1.0,
    ) -> str:
        """
        Download a submitted imagery order.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an item in the order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            item_id: A string representing the specific image identifiers e.g.
            "20221010T222611000_basic_0_TABI".

            destdir: A string (file path) representing the directory to which
            the imagery will be downloaded.

            retry_factor: A float that determines how retries will be handled.
            A factor of 0.5 means that only half the time specified by the
            "Retry-After" header will be observed before the download request
            is retried again. Defaults to 1.0.

        Returns:
            A string specifying the path the imagery has been downloaded to.

        """
        item_url = self.item_download_url(
            contract_id=contract_id,
            order_id=order_id,
            item_id=item_id,
            retry_factor=retry_factor,
        )["url"]

        response = self.make_request(method="GET", url=item_url)

        destfile = os.path.join(destdir, f"{item_id}.zip")
        data = raw_response_to_bytes(response)

        return bytes_to_file(data, destfile)

    def download_order(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: UUID,
        destdir: str,
        retry_factor: float = 1.0,
    ) -> str:
        """
        Downloads entire imagery order.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            destdir: A string (file path) representing the directory to which
            the imagery will be downloaded.

            retry_factor: A float that determines how retries will be handled.
            A factor of 0.5 means that only half the time specified by the
            "Retry-After" header will be observed before the download request
            is retried again. Defaults to 1.0.

        Returns:
            A string specifying the path the imagery has been downloaded to.
            All items will be downloaded into one ZIP file.
        """
        order_url = self.order_download_url(
            contract_id=contract_id, order_id=order_id, retry_factor=retry_factor
        )["url"]

        response = self.make_request(method="GET", url=order_url)

        destfile = os.path.join(destdir, f"{order_id}.zip")
        data = raw_response_to_bytes(response)

        return bytes_to_file(data, destfile)
