from datetime import datetime
from json import loads
from typing import Literal, Optional, Tuple, Union
from uuid import UUID

from .base import AbstractApi
from satellitevu.apis.orders import raw_response_to_bytes

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
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        **kwargs,
    ):
        """
        Creates a tasking feasibility request.

        Args:
            coordinates: An array of coordinates - (longitude, latitude) or
            (longitude, latitude, altitude).

            date_from: datetime representing the start date of the feasibility request.

            date_to: datetime representing the end date of the feasibility request.

            day_night_mode: String representing the mode of data capture. Allowed values
            include ["day", "night", "day-night"]. Defaults to "day-night".

        Returns:
            A dictionary containing properties of the feasibility request.
        """
        url = self.url("/tasking/feasibilities/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "satvu:day_night_mode": day_night_mode,
                **kwargs,
            },
        }

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

        if response.status != 202:
            raise Exception(f"Error - {response.status} : {response.text}")

        response_bytes = raw_response_to_bytes(response)
        return loads(response_bytes.read())

    def get_feasibility(self, *, id: Union[UUID, str]):
        """
        Retrieve the feasibility request with a given ID.

        Args:
            id: UUID representing the feasibility request e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the feasibility request.
        """
        response = self.make_request(
            method="GET",
            url=self.url(f"/tasking/feasibilities/{str(id)}"),
        )
        return response.json()

    def get_feasibility_response(self, *, id: Union[UUID, str]):
        """
        Retrieves the feasibility response for the feasibility request
        with a given id.

        Args:
            id: UUID representing the feasibility request e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing the feasibility response.
        """
        response = self.make_request(
            method="GET",
            url=self.url(f"/tasking/feasibilities/{str(id)}/response"),
        )
        return response.json()

    def list_feasibility_requests(
        self, *, per_page: int = 25, page_token: Optional[str] = None
    ):
        """
        Retrieves a list of your feasibility requests.

        Args:
            per_page: Number of results (defaults to 25) to be returned per page.

        Returns:
            A dictionary containing a list of feasibility requests and their properties.
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        response = self.make_request(
            method="GET", url=self.url(f"/tasking/feasibilities/?{query}")
        )
        return response.json()

    def create_order(
        self,
        *,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        **kwargs,
    ):
        """
        Creates a tasking order request.

        Args:
            coordinates: An array of coordinates - (longitude, latitude) or
            (longitude, latitude, altitude).

            date_from: datetime representing the start date of the order.

            date_to: datetime representing the end date of the order.

            day_night_mode: String representing the mode of data capture. Allowed values
            include ["day", "night", "day-night"]. Defaults to "day-night".

        Returns:
            A dictionary containing properties of the order created.
        """
        url = self.url("/tasking/orders/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "satvu:day_night_mode": day_night_mode,
                **kwargs,
            },
        }

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
        if response.status != 201:
            raise Exception(f"Error - {response.status} : {response.text}")

        return response.json()

    def get_order(self, *, order_id: Union[UUID, str]):
        """
        Retrieve the order with a given order_id.

        Args:
            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the order.
        """
        response = self.make_request(
            method="GET", url=self.url(f"/tasking/orders/{str(order_id)}")
        )
        return response.json()

    def list_orders(self, *, per_page: int = 25, page_token: Optional[str] = None):
        """
        Retrieves a list of your orders. The orders are returned sorted by creation
        date, with the most recent orders appearing first.

        Args:
            per_page: Number of results (defaults to 25) to be returned per page.

        Returns:
            A dictionary containing a list of orders and their properties.
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        response = self.make_request(
            method="GET", url=self.url(f"/tasking/orders/?{query}")
        )
        return response.json()

    def get_price(
        self,
        *,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
    ):
        """
        Returns the price for a set of ordering parameters.

        Args:
            coordinates: An array of coordinates.

            date_from: datetime representing the start date of the order.

            date_to: datetime representing the end date of the order.

        Returns:
            A dictionary containing keys: price, created_at where the price field
            indicates the price, in tokens, for the set of ordering parameters and
            created_at is the UTC datetime at which the price was calculated.

        """
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

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
        return response.json()


class OtmV2(AbstractApi):
    """
    Client interface to the OTM API located at
    https://api.satellitevu.com/otm/v2/docs.
    """

    api_path = "otm/v2"
    scopes = ["tasking:w"]

    def post_feasibility(
        self,
        *,
        contract_id: UUID,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        **kwargs,
    ):
        """
        Creates a tasking feasibility request.

        Args:
            contract_id: Associated ID of the Contract under which the feasibility
            request will be performed.

            coordinates: An array of coordinates - (longitude, latitude) or
            (longitude, latitude, altitude).

            date_from: datetime representing the start date of the feasibility request.

            date_to: datetime representing the end date of the feasibility request.

            day_night_mode: String representing the mode of data capture. Allowed values
            include ["day", "night", "day-night"]. Defaults to "day-night".

        Returns:
            A dictionary containing properties of the feasibility request.
        """
        url = self.url(f"{str(contract_id)}/tasking/feasibilities/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "satvu:day_night_mode": day_night_mode,
                **kwargs,
            },
        }

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

        if response.status != 202:
            raise Exception(f"Error - {response.status} : {response.text}")

        response_bytes = raw_response_to_bytes(response)

        return loads(response_bytes.read())

    def get_feasibility(self, *, contract_id: UUID, id: Union[UUID, str]):
        """
        Retrieve the feasibility request with a given ID.

        Args:
            contract_id: Associated ID of the Contract for the given feasibility
            request.

            id: UUID representing the feasibility request e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the feasibility request.
        """
        response = self.make_request(
            method="GET",
            url=self.url(f"{str(contract_id)}/tasking/feasibilities/{str(id)}"),
        )
        return response.json()

    def get_feasibility_response(self, *, contract_id: UUID, id: Union[UUID, str]):
        """
        Retrieves the feasibility response for the feasibility request
        with a given id.

        Args:
            contract_id: Associated ID of the Contract for the given feasibility
            request.

            id: UUID representing the feasibility request e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing the feasibility response.
        """
        response = self.make_request(
            method="GET",
            url=self.url(
                f"{str(contract_id)}/tasking/feasibilities/{str(id)}/response"
            ),
        )
        return response.json()

    def list_feasibility_requests(
        self, *, contract_id: UUID, per_page: int = 25, page_token: Optional[str] = None
    ):
        """
        Retrieves a list of your feasibility requests.

        Args:
            contract_id: Associated ID of the Contract for which all feasibility
            requests will be listed.

            per_page: Number of results (defaults to 25) to be returned per page.

        Returns:
            A dictionary containing a list of feasibility requests and their properties.
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        response = self.make_request(
            method="GET",
            url=self.url(f"{str(contract_id)}/tasking/feasibilities/?{query}"),
        )
        return response.json()

    def create_order(
        self,
        *,
        contract_id: UUID,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        **kwargs,
    ):
        """
        Creates a tasking order request.

        Args:
            contract_id: Associated ID of the Contract under which the tasking
            order will be submitted.

            coordinates: An array of coordinates - (longitude, latitude) or
            (longitude, latitude, altitude).

            date_from: datetime representing the start date of the order.

            date_to: datetime representing the end date of the order.

            day_night_mode: String representing the mode of data capture. Allowed values
            include ["day", "night", "day-night"]. Defaults to "day-night".

        Returns:
            A dictionary containing properties of the order created.
        """
        url = self.url(f"{str(contract_id)}/tasking/orders/")
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "satvu:day_night_mode": day_night_mode,
                **kwargs,
            },
        }

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

        if response.status != 201:
            raise Exception(f"Error - {response.status} : {response.text}")

        return response.json()

    def get_order(self, *, contract_id: UUID, order_id: Union[UUID, str]):
        """
        Retrieve the order with a given order_id.

        Args:
            contract_id: Associated ID of the Contract under which the tasking
            order is stored.

            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            A dictionary containing properties of the order.
        """
        response = self.make_request(
            method="GET",
            url=self.url(f"{str(contract_id)}/tasking/orders/{str(order_id)}"),
        )
        return response.json()

    def list_orders(
        self, *, contract_id: UUID, per_page: int = 25, page_token: Optional[str] = None
    ):
        """
        Retrieves a list of your orders. The orders are returned sorted by creation
        date, with the most recent orders appearing first.

        Args:
            contract_id: Associated ID of the Contract under which all tasking
            orders will be listed.

            per_page: Number of results (defaults to 25) to be returned per page.

        Returns:
            A dictionary containing a list of orders and their properties.
        """
        query = f"per_page={per_page}"
        if page_token:
            query += f"&token={page_token}"

        response = self.make_request(
            method="GET", url=self.url(f"{str(contract_id)}/tasking/orders/?{query}")
        )
        return response.json()

    def get_price(
        self,
        *,
        contract_id: UUID,
        coordinates: Union[Tuple[float, float], Tuple[float, float, float]],
        date_from: datetime,
        date_to: datetime,
    ):
        """
        Returns the price for a set of ordering parameters.

        Args:
            contract_id: Associated ID of the Contract for which the pricebook
            will be listed.

            coordinates: An array of coordinates.

            date_from: datetime representing the start date of the order.

            date_to: datetime representing the end date of the order.

        Returns:
            A dictionary containing keys: price, created_at where the price field
            indicates the price, in tokens, for the set of ordering parameters and
            created_at is the UTC datetime at which the price was calculated.

        """
        url = self.url(f"{str(contract_id)}/tasking/price/")
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

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
        return response.json()
