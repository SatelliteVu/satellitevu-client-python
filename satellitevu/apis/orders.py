from typing import List, Union

from .base import AbstractApi


class OrdersV1(AbstractApi):
    _api_path = "orders/v1"

    def submit(self, item_ids: Union[List[str], str]):
        url = self._url("/")

        if isinstance(item_ids, str):
            item_ids = [item_ids]

        return self.client.post(url=url, json={"item_id": item_ids})
