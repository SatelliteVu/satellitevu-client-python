import os
import shutil
import tempfile
from io import BytesIO
from typing import Dict, List, Union
from uuid import UUID

from satellitevu.http.base import ResponseWrapper

from .base import AbstractApi


def raw_response_to_bytes(response: ResponseWrapper) -> BytesIO:
    """
    Converts the raw response data from a request into a bytes object.
    """
    raw_response = response.raw

    if isinstance(raw_response, bytes):
        data = BytesIO(raw_response)
    elif hasattr(raw_response, "read"):
        data = BytesIO(raw_response.read())
    elif hasattr(raw_response, "iter_content"):
        data = BytesIO()
        for chunk in raw_response.iter_content():
            data.write(chunk)
        data.seek(0)
    else:
        raise Exception(
            (
                "Cannot convert response object with raw type"
                f"{type(raw_response)} into byte stream."
            )
        )

    return data


def bytes_to_file(data: BytesIO, destfile: str) -> str:
    """
    Converts bytes into a file object at the specified location.
    """
    with open(destfile, "wb+") as f:
        f.write(data.getbuffer())

    return destfile


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
            raise Exception(f"Error - {response.status} : {response.text}")

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
            raise Exception(f"Error - {response.status} : {response.text}")

        return response.json()

    def submit(self, *, contract_id: Union[UUID, str], item_ids: Union[List[str], str]):
        """
        Submit an imagery order for items present in the SatVu archive.

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

    def item_download_url(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: Union[UUID, str],
        item_id: str,
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

        Returns:
            A dictionary containing the url which the image can be downloaded from.
        """
        url = self.url(f"/{contract_id}/{order_id}/{item_id}/download?redirect=False")

        response = self.make_request(method="GET", url=url)
        return response.json()

    def download_item(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: UUID,
        item_id: str,
        destdir: str,
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

            destfile: A string (file path) representing the directory to which
            the imagery will be downloaded.

        Returns:
            A string specifying the path the imagery has been downloaded to.

        """
        item_url = self.item_download_url(
            contract_id=contract_id, order_id=order_id, item_id=item_id
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
    ) -> str:
        """
        Downloads entire imagery order into one ZIP file.

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which an order is associated with.

            order_id: String or UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            destdir: String specifying path of the directory where imagery will
            be downloaded to

        Returns:
            A string specifying the path the imagery has been downloaded to.
            All items will be downloaded into one ZIP file.
        """
        order_details = self.get_order_details(
            contract_id=contract_id, order_id=order_id
        )

        order_id = order_details["id"]
        item_ids = [i["properties"]["item_id"] for i in order_details["features"]]

        return self._save_order_to_zip(destdir, contract_id, order_id, item_ids)

    def _save_order_to_zip(
        self,
        destdir: str,
        contract_id: Union[UUID, str],
        order_id: UUID,
        item_ids: List[str],
    ):
        destzip = os.path.join(destdir, f"SatVu_{order_id}")
        with tempfile.TemporaryDirectory(dir=destdir) as tmpdir:
            for item_id in item_ids:
                self.download_item(
                    contract_id=contract_id,
                    order_id=order_id,
                    item_id=item_id,
                    destdir=tmpdir,
                )

            zipfile = shutil.make_archive(destzip, "zip", tmpdir)

        return zipfile
