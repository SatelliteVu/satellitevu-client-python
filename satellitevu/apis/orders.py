import os
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from .base import AbstractApi


class OrdersV1(AbstractApi):
    _api_path = "orders/v1"

    def submit(self, item_ids: Union[List[str], str]):
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
        url = self._url(f"/{order_id}/{item_id}/download?redirect=False")

        redirect_resp = self.client.request(method="GET", url=url)
        redirect_json = redirect_resp.json()

        if redirect is False:
            return redirect_json

        response = self.client.request(method="GET", url=redirect_json["url"])
        data = BytesIO(response.raw.read())

        if destfile is None:
            downloads_path = str(Path.home() / "Downloads")
            print("Zip file will be downloaded to the Downloads folder")
            destfile = os.path.join(downloads_path, f"{item_id}.zip")

        with open(destfile, "wb+") as f:
            f.write(data.getbuffer())

        return destfile
