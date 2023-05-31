from datetime import datetime
from typing import Optional, Tuple, Union
from uuid import UUID

from .base import AbstractApi

# TODO: Tests


class OtmV1(AbstractApi):
    """
    Client interface to the OTM API located at
    https://api.satellitevu.com/otm/v1/docs.
    """

    api_path = "otm/v1"
    scopes = ["tasking:w"]

    def post_feasibility(
        self,
        *,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
    ):
        """
        TODO: Docs
        """
        url = self.url("/tasking/feasibilities/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}"
            },
        }

        return self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

    def get_feasibility(self, *, id: Union[UUID, str]):
        """
        TODO: Docs
        """
        return self.make_request(
            method="GET",
            url=self.url(f"/tasking/feasibilities/{str(id)}"),
        )

    def get_feasibility_response(self, *, id: Union[UUID, str]):
        """
        TODO: Docs
        """
        return self.make_request(
            method="GET",
            url=self.url(f"/tasking/feasibilities/{str(id)}/response"),
        )

    def list_feasibility_requests(
        self, *, per_page: int = 25, page_token: Optional[str] = None
    ):
        """
        TODO: Docs
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        return self.make_request(
            method="GET", url=self.url(f"/tasking/feasibilities/?{query}")
        )

    def create_order(
        self,
        *,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
    ):
        """
        TODO: Docs
        """
        url = self.url("/tasking/orders/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}"
            },
        }

        return self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

    def get_order(self, *, order_id: Union[UUID, str]):
        """
        TODO: Docs
        """
        return self.make_request(
            method="GET", url=self.url(f"/tasking/orders/{str(order_id)}")
        )

    def list_orders(self, *, per_page: int = 25, page_token: Optional[str] = None):
        """
        TODO: Docs
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        return self.make_request(
            method="GET", url=self.url(f"/tasking/orders/?{query}")
        )

    def get_price(
        self,
        *,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
    ):
        url = self.url("/tasking/price/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}"
            },
        }

        return self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
