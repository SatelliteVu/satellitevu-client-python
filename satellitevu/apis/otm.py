from datetime import datetime
from typing import Any, Literal, List, Optional, Tuple, Union
from uuid import UUID

from .base import AbstractApi


class OtmV2(AbstractApi):
    """
    Client interface to the OTM API located at
    https://api.satellitevu.com/otm/v2/docs.
    """

    api_path = "otm/v2"
    scopes = []

    def post_feasibility(
        self,
        *,
        contract_id: Union[UUID, str],
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

            day_night_mode: String representing the mode of data capture. Allowed
            values are ["day", "night", "day-night"]. Defaults to "day-night".


        Kwargs:
            max_cloud_cover: Optional integer representing the maximum threshold
            of acceptable cloud coverage. Measured in percent. Defaults to 100.

            min_off_nadir: Optional integer representing the minimum angle from
            the sensor between nadir and the scene center. Measured in decimal
            degrees. Defaults to 0.

            max_off_nadir: Optional integer representing the maximum angle from
            the sensor between nadir and the scene center. Measured in decimal
            degrees. Must be larger than min_off_nadir. Defaults to 45.

            min_gsd: Optional integer representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to 3.5.

            max_gsd: Optional integer representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to 6.8.

            Please note that min/max off nadir and min/max gsd are mutually exclusive.
            You must pick either the off nadir angle or gsd as parameters.

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

        return response.json()

    def get_feasibility(self, *, contract_id: Union[UUID, str], id: Union[UUID, str]):
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

    def get_feasibility_response(
        self, *, contract_id: Union[UUID, str], id: Union[UUID, str]
    ):
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
        self,
        *,
        contract_id: Union[UUID, str],
        per_page: int = 25,
        page_token: Optional[str] = None,
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
        contract_id: Union[UUID, str],
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

            day_night_mode: String representing the mode of data capture. Allowed
            values are ["day", "night", "day-night"]. Defaults to "day-night".

        Kwargs:
            max_cloud_cover: Optional integer representing the maximum threshold
            of acceptable cloud coverage. Measured in percent. Defaults to 100.

            min_off_nadir: Optional integer representing the minimum angle from
            the sensor between nadir and the scene center. Measured in decimal
            degrees. Defaults to 0.

            max_off_nadir: Optional integer representing the maximum angle from
            the sensor between nadir and the scene center. Measured in decimal
            degrees. Must be larger than min_off_nadir. Defaults to 45.

            min_gsd: Optional integer representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to 3.5.

            max_gsd: Optional integer representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to 6.8.

            Please note that min/max off nadir and min/max gsd are mutually exclusive.
            You must pick either the off nadir angle or gsd as parameters.

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

    def get_order(self, *, contract_id: Union[UUID, str], order_id: Union[UUID, str]):
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
        self,
        *,
        contract_id: Union[UUID, str],
        per_page: int = 25,
        page_token: Optional[str] = None,
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
        contract_id: Union[UUID, str],
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

    def search(
        self,
        contract_id: Union[str, UUID],
        page_token: Optional[str] = None,
        per_page: int = 25,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        date_range: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        properties: Optional[dict] = None,
        intersects: Optional[Any] = None,
        sort_by: Optional[List[dict]] = None,
    ):
        """
        Performs a search across all feasibility and orders associated with a
        contract.

        Args:
            contract_id: Associated ID of the Contract under which the search
            request will be performed.

            page_token: Optional string key used to return specific page of results.
            Defaults to None -> assumes page 0.

            per_page: Number of results (defaults to 25) to be returned per page.

            collections: List of strings specifying the collections within which
            to search. Allowed values are:
            [ "feasibility", "feasibility|response|%", "orders", "otm|orders|%" ]

            ids: List of strings specifying the ids within which
            to search.

            datetime: Optional string specifying a closed datetime range within
            which to search e.g. "2023-03-22T12:50:24+01:00/2023-03-29T12:50:24+01:00"
            Assumed to be UTC if timezone offset is not given. This datetime range
            corresponds directly to the datetime property associated with the
            order/feasibility request/response item.

            created_at: Optional string specifying a closed datetime range within
            which to search e.g. "2023-03-22T12:50:24+01:00/2023-03-29T12:50:24+01:00"
            Assumed to be UTC if timezone offset is not given. This datetime range
            describes when the database entries are created.

            updated_at: Optional string specifying a closed datetime range within
            which to search e.g. "2023-03-22T12:50:24+01:00/2023-03-29T12:50:24+01:00"
            Assumed to be UTC if timezone offset is not given. This datetime range
            describes when database entries are updated.

            properties: Optional dictionary specifying the filterable fields and
            value. Fields can be filtered by 'status', 'min_off_nadir',
            'max_off_nadir', 'min_gsd', 'max_gsd'.
            Examples: {"status" : "failed", "max_gsd" : 6.5, "min_off_nadir": 35}

            intersects: Optional dictionary with keys "coordinates" and "geometry"
            type that search results intersect with. Available geometry types include:
            "Point","MultiPoint", "LineString", "MultiLineString", "Polygon",
            "MultiPolygon". For example:
            intersects = {"coordinates":[-1.065151, 51.163899], "type" : "Point"}.

            sortby: List of parameters specifying the field and direction
            ('asc', 'desc') the results are sorted by. Currently only the 'status'
            field is sortable e.g. [{"field": "status", "direction": "desc"}].
        """
        url = self.url(f"{str(contract_id)}/search/")
        payload = {
            "token": page_token,
            "limit": per_page,
            "collections": collections,
            "ids": ids,
            "datetime": date_range,
            "created_at": created_at,
            "updated_at": updated_at,
            "properties": properties,
            "intersects": intersects,
            "sort_by": sort_by,
        }

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
        return response.json()
