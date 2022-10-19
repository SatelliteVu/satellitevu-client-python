import os
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from .base import AbstractApi


class OrdersV1(AbstractApi):
    """
    Client interface to the Orders API located at
    https://api.qa.satellitevu.com/orders/v1/docs.
    """

    _api_path = "orders/v1"

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

    def download(
        self,
        order_id: UUID,
        item_id: str,
        redirect: bool = True,
        destfile: Optional[str] = None,
    ) -> Union[Dict, str]:
        """
        Download a submitted imagery order.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

            item_id: A string representing the specific image identifiers e.g.
            "20221010T222611000_basic_0_TABI".

            redirect: Boolean value (default=True).

            destfile: An optional string representing the path to which the imagery
            will be downloaded to. If not specified, the imagery will be downloaded
            to the user's Downloads directory and labelled as <item_id>.zip.

        Returns:
            If redirect is False, a dictionary containing the url which the
            image can be downloaded from.

            If redirect is True, a string is returned specifying the path the
            imagery has been downloaded to.

        """
        url = self._url(f"/{order_id}/{item_id}/download?redirect=False")

        redirect_resp = self.client.request(method="GET", url=url)
        redirect_json = redirect_resp.json()

        if redirect is False:
            return redirect_json

        response = self.client.request(method="GET", url=redirect_json["url"])
        bytes = response.raw

        if hasattr(bytes, "read"):
            data = BytesIO(bytes.read())
        elif hasattr(bytes, "iter_content"):
            data = BytesIO()
            for chunk in response.raw.iter_content():
                data.read(chunk)

        if destfile is None:
            downloads_path = str(Path.home() / "Downloads")
            print("Zip file will be downloaded to the Downloads folder")
            destfile = os.path.join(downloads_path, f"{item_id}.zip")

        with open(destfile, "wb+") as f:
            f.write(data.getbuffer())

        return destfile
