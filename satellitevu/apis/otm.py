import os
from datetime import datetime
from time import sleep
from typing import Any, List, Literal, Optional, Tuple, Union, Dict
from uuid import UUID

from .base import AbstractApi
from .exceptions import (
    OTMOrderCancellationError,
    OTMFeasibilityError,
    OTMOrderError,
    OTMParametersError,
)
from .helpers import raw_response_to_bytes, bytes_to_file

MAX_CLOUD_COVER_DEFAULT = 15
MIN_OFF_NADIR_RANGE = [0, 45]
MAX_OFF_NADIR_RANGE = MIN_OFF_NADIR_RANGE
MIN_GSD_RANGE = [3.5, 6.8]
MAX_GSD_RANGE = MIN_GSD_RANGE


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
        product: Literal["standard", "assured"] = "standard",
        max_cloud_cover: Optional[int] = MAX_CLOUD_COVER_DEFAULT,
        min_off_nadir: Optional[int] = None,
        max_off_nadir: Optional[int] = None,
        min_gsd: Optional[float] = None,
        max_gsd: Optional[float] = None,
        **kwargs,
    ):
        f"""
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

            product: String representing a tasking option. Selecting "assured"
            allows visibility of all passes within the datetime interval. The
            user must accept all cloud cover risk.

            max_cloud_cover: Optional integer, ranging between [0,100] representing
            the maximum threshold of acceptable cloud coverage. Measured in percent.
            Defaults to {MAX_CLOUD_COVER_DEFAULT}.

            min_off_nadir: Optional integer, ranging between {MIN_OFF_NADIR_RANGE},
            representing the minimum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Defaults to None.

            max_off_nadir: Optional integer, ranging between {MAX_OFF_NADIR_RANGE},
            representing the maximum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Must be larger than
            min_off_nadir. Defaults to None.

            min_gsd: Optional float representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to None.

            max_gsd: Optional float, ranging between {MAX_GSD_RANGE},
            representing the minimum ground sample distance value. Measured in
            metres, this value reflects the square root of the area of the pixel
            size projected onto the earth. Defaults to None.

            Please note that min/max off nadir and min/max gsd are mutually exclusive.
            You must pick either the off nadir angle or gsd as parameters.

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            A dictionary containing properties of the feasibility request.
        """
        url = self.url(f"{str(contract_id)}/tasking/feasibilities/")

        if product == "standard" and not any(
            [min_gsd, max_gsd, min_off_nadir, max_off_nadir]
        ):
            raise OTMParametersError(
                "One pair of Off Nadir or GSD values must be specified for a "
                "standard priority feasibility request."
            )

        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "product": product,
                **kwargs,
            },
        }

        if product == "standard":
            payload["properties"].update(
                {
                    "satvu:day_night_mode": day_night_mode,
                    "max_cloud_cover": max_cloud_cover,
                }
            )

            for k, v in {
                "min_off_nadir": min_off_nadir,
                "max_off_nadir": max_off_nadir,
                "min_gsd": min_gsd,
                "max_gsd": max_gsd,
            }.items():
                if v is None:
                    continue
                payload["properties"].update({k: v})

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

        if response.status != 202:
            raise OTMFeasibilityError(response.status, response.text)

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

            page_token: Optional string key used to return specific page of results.
            Defaults to None -> assumes page 0.

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
        coordinates: Optional[
            Union[Tuple[float, float], Tuple[float, float, float]]
        ] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        product: Literal["standard", "assured"] = "standard",
        max_cloud_cover: Optional[int] = MAX_CLOUD_COVER_DEFAULT,
        min_off_nadir: Optional[int] = None,
        max_off_nadir: Optional[int] = None,
        min_gsd: Optional[float] = None,
        max_gsd: Optional[float] = None,
        addon_withhold: Optional[str] = None,
        signature: Optional[str] = None,
        **kwargs,
    ):
        f"""
        Creates a tasking order request.

        Args:
            contract_id: Associated ID of the Contract under which the tasking
            order will be submitted.

            coordinates: An array of coordinates - (longitude, latitude) or
            (longitude, latitude, altitude). Only required for orders with
            standard priority. Defaults to None.

            date_from: Datetime representing the start date of the order. Required
            for orders with standard priority. Defaults to None.

            date_to: Datetime representing the end date of the order. Required for
            orders with standard priority. Defaults to None

            day_night_mode: String representing the mode of data capture. Allowed
            values are ["day", "night", "day-night"]. Defaults to "day-night".

            product: String representing a tasking option. Selecting "assured"
            allows visibility of all passes within the datetime interval. The
            user must accept all cloud cover risk.

            signature: String representing a signature token required for orders
            with assured priority. Defaults to None.

            max_cloud_cover: Optional integer, ranging between [0,100] representing
            the maximum threshold of acceptable cloud coverage. Measured in percent.
            Defaults to {MAX_CLOUD_COVER_DEFAULT}.

            min_off_nadir: Optional integer, ranging between {MIN_OFF_NADIR_RANGE},
            representing the minimum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Defaults to None.

            max_off_nadir: Optional integer, ranging between {MAX_OFF_NADIR_RANGE},
            representing the maximum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Must be larger than
            min_off_nadir. Defaults to None.

            min_gsd: Optional float representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to None.

            max_gsd: Optional float, ranging between {MAX_GSD_RANGE},
            representing the minimum ground sample distance value. Measured in
            metres, this value reflects the square root of the area of the pixel
            size projected onto the earth. Defaults to None.

            Please note that min/max off nadir and min/max gsd are mutually exclusive.
            You must pick either the off nadir angle or gsd as parameters.

            addon_withhold: Optional ISO8601 string describing the duration that an order
            will be withheld from the public catalog. Withhold options are specific
            to the contract. If not specified, the option will be set to the default
            specified in the relevant contract. Example values are: ["0d", "3m", "1y"]

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            A dictionary containing properties of the order created.
        """
        url = self.url(f"{str(contract_id)}/tasking/orders/")

        payload = {"properties": {"product": product}}

        if addon_withhold:
            payload["properties"].update({"addon:withhold": addon_withhold})

        if product == "standard":
            if not "coordinates":
                raise OTMParametersError(
                    "`coordinates` must be specified for a standard priority order"
                )
            if not date_from or not date_to:
                raise OTMParametersError(
                    "`date_to` and `date_from` must be specified for a standard "
                    "priority order"
                )

            if not any([min_gsd, max_gsd, min_off_nadir, max_off_nadir]):
                raise OTMParametersError(
                    "One pair of Off Nadir or GSD values must be specified for a "
                    "standard priority order."
                )

        if product == "assured":
            if not signature:
                raise Exception(
                    "Orders with assured priority must have a signature token."
                )
            payload["properties"].update({"signature": signature})

        else:
            payload["properties"].update(
                {
                    "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                    "satvu:day_night_mode": day_night_mode,
                    "max_cloud_cover": max_cloud_cover,
                }
            )

            payload.update(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coordinates,
                    },
                }
            )
            payload["properties"].update(kwargs)

            for k, v in {
                "min_off_nadir": min_off_nadir,
                "max_off_nadir": max_off_nadir,
                "min_gsd": min_gsd,
                "max_gsd": max_gsd,
            }.items():
                if v is None:
                    continue
                payload["properties"].update({k: v})

        response = self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )

        if response.status != 201:
            raise OTMOrderError(response.status, response.text)

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

    def cancel_order(
        self, *, contract_id: Union[UUID, str], order_id: Union[UUID, str]
    ):
        """
        Cancel an order with a given order_id. Raises OTMOrderCancellationError
        if returned status code is not 204.

        Args:
            contract_id: Associated ID of the Contract under which the tasking
            order is stored.

            order_id: UUID representing the order id e.g.
            "2009466e-cccc-4712-a489-b09aeb772296".

        Returns:
            None
        """
        response = self.make_request(
            method="POST",
            url=self.url(f"{str(contract_id)}/tasking/orders/{str(order_id)}/cancel"),
        )
        if response.status != 204:
            raise OTMOrderCancellationError(response.status, response.text)

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

            page_token: Optional string key used to return specific page of results.
            Defaults to None -> assumes page 0.

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
        day_night_mode: Literal["day", "night", "day-night"] = "day-night",
        product: Literal["standard", "assured"] = "standard",
        max_cloud_cover: Optional[int] = None,
        min_off_nadir: Optional[int] = None,
        max_off_nadir: Optional[int] = None,
        min_gsd: Optional[float] = None,
        max_gsd: Optional[float] = None,
        **kwargs,
    ):
        """
        Returns the price for a set of ordering parameters.

        Args:
            contract_id: Associated ID of the Contract for which the pricebook
            will be listed.

            coordinates: An array of coordinates.

            date_from: datetime representing the start date of the order.

            date_to: datetime representing the end date of the order.

            day_night_mode: String representing the mode of data capture. Allowed
            values are ["day", "night", "day-night"]. Defaults to "day-night".

            product: String representing a tasking option. Selecting "assured"
            allows visibility of all passes within the datetime interval. The
            user must accept all cloud cover risk.

            max_cloud_cover: Optional integer, ranging between [0,100] representing
            the maximum threshold of acceptable cloud coverage. Measured in percent.
            Defaults to {MAX_CLOUD_COVER_DEFAULT}.

            min_off_nadir: Optional integer, ranging between {MIN_OFF_NADIR_RANGE},
            representing the minimum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Defaults to None.

            max_off_nadir: Optional integer, ranging between {MAX_OFF_NADIR_RANGE},
            representing the maximum angle from the sensor between nadir and the
            scene center. Measured in decimal degrees. Must be larger than
            min_off_nadir. Defaults to None.

            min_gsd: Optional float representing the minimum ground sample
            distance value. Measured in metres, this value reflects the square
            root of the area of the pixel size projected onto the earth. Defaults
            to None.

            max_gsd: Optional float, ranging between {MAX_GSD_RANGE},
            representing the minimum ground sample distance value. Measured in
            metres, this value reflects the square root of the area of the pixel
            size projected onto the earth. Defaults to None.

            Please note that min/max off nadir and min/max gsd are mutually exclusive.
            You must pick either the off nadir angle or gsd as parameters.

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            A dictionary containing keys: price, created_at where the price field
            indicates the price, in tokens, for the set of ordering parameters and
            created_at is the UTC datetime at which the price was calculated.

        """
        url = self.url(f"{str(contract_id)}/tasking/price/")

        if product == "standard" and not any(
            [min_gsd, max_gsd, min_off_nadir, max_off_nadir]
        ):
            raise OTMParametersError(
                "One pair of Off Nadir or GSD values must be specified for a "
                "standard priority order."
            )

        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "datetime": f"{date_from.isoformat()}/{date_to.isoformat()}",
                "product": product,
                **kwargs,
            },
        }

        if product == "standard":
            payload["properties"].update(
                {
                    "satvu:day_night_mode": day_night_mode,
                    "max_cloud_cover": max_cloud_cover,
                }
            )

            for k, v in {
                "min_off_nadir": min_off_nadir,
                "max_off_nadir": max_off_nadir,
                "min_gsd": min_gsd,
                "max_gsd": max_gsd,
            }.items():
                if v is None:
                    continue
                payload["properties"].update({k: v})

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

            date_range: Optional string specifying a closed datetime range within
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

            sort_by: List of parameters specifying the field and direction
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

    def order_download_url(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: Union[UUID, str],
        retry_factor: float = 1.0,
    ) -> Dict:
        """
        Finds the download url for a submitted tasking order.

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
        url = self.url(
            f"/{contract_id}/tasking/orders/{order_id}/download?redirect=False"
        )

        return self._download_request(url, retry_factor=retry_factor)

    def download_order(
        self,
        *,
        contract_id: Union[UUID, str],
        order_id: UUID,
        destdir: str,
        retry_factor: float = 1.0,
    ):
        """
        Downloads tasking order.

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
