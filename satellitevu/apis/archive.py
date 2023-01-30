from datetime import datetime
from typing import Any, Optional

from .base import AbstractApi


class ArchiveV1(AbstractApi):
    """
    Client interface to the Archive API located at
    https://api.satellitevu.com/archive/v1/docs.
    """

    api_path = "archive/v1"
    scopes = []

    def search(
        self,
        *,
        intersects: Optional[Any] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit=10,
        page_token: Optional[str] = None,
        **kwargs,
    ):
        """
        Perform a search on Satellite Vu's STAC. Relevant documentation is located
        at https://api.satellitevu.com/archive/v1/docs#operation/Search_search_post

        Kwargs:
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

            sortby: List of parameters specifying the field and direction the results
            are sorted by e.g. [{"field": "datetime", "direction": "desc"}].

        Returns:
            An instance of ResponseWrapper where the .json() method returns a
            FeatureCollection (dictionary containing keys: "type", "features",
            "link", "context") of the catalogue items fulfilled by the search
            criteria.

        """
        url = self.url("/search")
        payload = {
            **kwargs,
            "intersects": intersects,
            "limit": limit,
            "token": page_token,
            "datetime": "/".join(
                filter(
                    lambda x: x,
                    [
                        date_from and date_from.isoformat(),
                        date_to and date_to.isoformat(),
                    ],
                )
            ),
        }

        return self.make_request(
            method="POST", url=url, json={k: v for k, v in payload.items() if v}
        )
