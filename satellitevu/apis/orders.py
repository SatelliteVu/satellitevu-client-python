from typing import List, Union
from uuid import UUID

from .base import AbstractApi


class OrdersV1(AbstractApi):
    _api_path = "orders/v1"

    def submit(self, item_ids: Union[List[str], str]):
        url = self._url("/")

        if isinstance(item_ids, str):
            item_ids = [item_ids]

        return self.client.post(url=url, json={"item_id": item_ids})

    def download(self, order_id: UUID, item_id: str, redirect: bool = True):
        url = self._url(f"/{order_id}/{item_id}/download?{redirect=}")

        return self.client.request(method="GET", url=url)
