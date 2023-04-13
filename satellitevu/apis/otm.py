from datetime import datetime
from typing import Tuple, Union
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
