from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from uuid import UUID

from .base import AbstractApi

filterConstruct = filter


class CatalogV1(AbstractApi):
    """
    Client interface to the Catalog API located at
    https://api.satellitevu.com/catalog/v1/docs.
    """

    api_path = "catalog/v1"
    scopes = []

    def search(
        self,
        *,
        contract_id: Union[UUID, str],
        intersects: Optional[Any] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = 10,
        bbox: Optional[List[float]] = None,
        ids: Optional[List[str]] = None,
        collections: Optional[List[str]] = None,
        sort_by: Optional[List[dict]] = None,
        filter: Optional[dict] = None,
        page_token: Optional[str] = None,
        **kwargs,
    ):
        """
        Perform a search on Satellite Vu's STAC. Relevant documentation is located
        at https://api.satellitevu.com/catalog/v1/docs#operation/post-search

        Args:
            contract_id: String or UUID representing the ID of the Contract
            which a search is performed with.

            intersects: Optional dictionary with keys "coordinates" and "geometry"
            type that search results intersect with. Available geometry types include:
            "Point","MultiPoint", "LineString", "MultiLineString", "Polygon",
            "MultiPolygon". For example:
            intersects = {"coordinates":[-1.065151, 51.163899], "type" : "Point"}.

            date_from: Optional datetime representing the start date of the search.

            date_to: Optional datetime representing the end date of the search.

            limit:  Number of search results (defaults to 10) to be returned.

            bbox: List of points (min longitude, min latitude, max longitude,
            max latitude) specifying a bounding box to search within.

            ids: List of strings specifying the desired STAC identifiers
            e.g. ["20221010T222611000_basic_0_TABI"].

            collections: List of strings specifying the collections within which
            to search. Values include "basic" and "relative".

            sort_by: List of parameters specifying the field and direction the results
            are sorted by e.g. [{"field": "datetime", "direction": "desc"}].

            page_token: Optional string key used to return specific page of results.
            Defaults to None -> assumes page 0.

        Kwargs:
            Allows sending additional parameters that are supported by the API but not
            added to this SDK yet.

        Returns:
            An instance of ResponseWrapper where the .json() method returns a
            FeatureCollection (dictionary containing keys: "type", "features",
            "link", "context") of the catalog items fulfilled by the search
            criteria.

        """
        url = self.url(f"/{contract_id}/search")
        payload = {
            "intersects": intersects,
            "limit": limit,
            "datetime": "/".join(
                filterConstruct(
                    lambda x: x,
                    [
                        date_from and date_from.astimezone(timezone.utc).isoformat(),
                        date_to and date_to.astimezone(timezone.utc).isoformat(),
                    ],
                )
            ),
            "bbox": bbox,
            "ids": ids,
            "collections": collections,
            "sort_by": sort_by,
            "token": page_token,
            "filter": filter,
            **kwargs,
        }

        return self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
