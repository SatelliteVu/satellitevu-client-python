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
        raise Exception("Cannot convert Response object into byte stream.")

    return data


def bytes_to_file(data: BytesIO, destfile: str) -> str:
    """
    Converts bytes into a file object at the specified location.
    """
    with open(destfile, "wb+") as f:
        f.write(data.getbuffer())

    return destfile


class OrdersV1(AbstractApi):
    """
    Client interface to the Orders API located at
    https://api.qa.satellitevu.com/orders/v1/docs.
    """

    _api_path = "orders/v1"

    def get_order_details(self, order_id: UUID) -> Dict:
        """
        Retrieve details of an imagery order.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the order.
        """
        url = self._url(f"/{order_id}")
        response = self.client.request(method="GET", url=url)

        if response.status != 200:
            raise Exception(f"Error - {response.status} : {response.text}")

        return response.json()

    def submit(self, item_ids: Union[List[str], str]):
        """
        Submit an imagery order for items present in the Satellite Vu archive.

        Args:
            item_ids: A string or list of strings representing the image
            identifiers. For example: "20221005T214049000_basic_0_TABI" or
            ["20221005T214049000_basic_0_TABI, "20221010T222611000_basic_0_TABI"].

        Returns:
            A dictionary containing keys: id, type, features where the id field
            corresponds to an order id and features map to an array of imagery
            items described with conformity to the STAC specification.

        """
        url = self._url("/")

        if isinstance(item_ids, str):
            item_ids = [item_ids]

        return self.client.post(url=url, json={"item_id": item_ids})

    def item_download_url(
        self,
        order_id: UUID,
        item_id: str,
    ) -> Dict:
        """
        Finds the download url for an item in a submitted imagery order.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            item_id: A string representing the specific image identifiers e.g.
            "20221010T222611000_basic_0_TABI".

        Returns:
            A dictionary containing the url which the image can be downloaded from.
        """
        url = self._url(f"/{order_id}/{item_id}/download?redirect=False")

        response = self.client.request(method="GET", url=url)
        return response.json()

    def download_item(self, order_id: UUID, item_id: str, destdir: str) -> str:
        """
        Download a submitted imagery order.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            item_id: A string representing the specific image identifiers e.g.
            "20221010T222611000_basic_0_TABI".

            destfile: A string (file path) representing the directory to which
            the imagery will be downloaded.

        Returns:
            A string specifying the path the imagery has been downloaded to.

        """
        item_url = self.item_download_url(order_id, item_id)["url"]

        response = self.client.request(method="GET", url=item_url)

        destfile = os.path.join(destdir, f"{item_id}.zip")
        data = raw_response_to_bytes(response)

        return bytes_to_file(data, destfile)

    def download_order(self, order_id: UUID, destdir: str) -> str:
        """
        Downloads entire imagery order into one ZIP file.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            destdir: String specifying path of the directory where imagery will
            be downloaded to

        Returns:
            A string specifying the path the imagery has been downloaded to.
            All items will be downloaded into one ZIP file.
        """
        order_details = self.get_order_details(order_id)

        order_id = order_details["id"]
        item_ids = [i["properties"]["item_id"] for i in order_details["features"]]

        return self._save_order_to_zip(destdir, order_id, item_ids)

    def _save_order_to_zip(self, destdir: str, order_id: UUID, item_ids: List[str]):
        destzip = os.path.join(destdir, f"SatelliteVu_{order_id}")
        with tempfile.TemporaryDirectory(dir=destdir) as tmpdir:
            for item_id in item_ids:
                self.download_item(order_id, item_id, tmpdir)

            zipfile = shutil.make_archive(destzip, "zip", tmpdir)

        return zipfile
