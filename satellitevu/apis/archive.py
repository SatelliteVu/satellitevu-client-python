from datetime import datetime
from typing import Any, Optional

from .base import AbstractApi


class ArchiveV1(AbstractApi):
    _api_path = "archive/v1"

    def search(
        self,
        *,
        intersects: Optional[Any] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit=25,
        page_token: Optional[str] = None,
        **kwargs,
    ):
        url = self._url("/search")
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

        return self.client.post(
            url,
            json={k: v for k, v in payload.items() if v},
        )
