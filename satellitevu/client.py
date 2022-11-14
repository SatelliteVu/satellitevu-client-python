from typing import Optional, Union

from satellitevu.apis.archive import ArchiveV1
from satellitevu.apis.orders import OrdersV1
from satellitevu.auth import AbstractCache, Auth
from satellitevu.config import GATEWAY
from satellitevu.http import AbstractClient, UrllibClient


class Client:
    _client: AbstractClient
    _gateway_url: str

    auth: Auth

    archive_v1: ArchiveV1
    orders_v1: OrdersV1

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        audience: Optional[str] = None,
        cache: Optional[AbstractCache] = None,
        auth_url: Optional[str] = None,
        http_client: Optional[AbstractClient] = None,
        gateway_url: Optional[str] = None,
    ):
        self._gateway_url = gateway_url or GATEWAY
        self._client = http_client or self._setup_client()

        self.auth = Auth(
            client_id=client_id,
            client_secret=client_secret,
            audience=audience,
            cache=cache,
            auth_url=auth_url,
            client=self._client,
        )
        self._client.set_auth(self._gateway_url, self.auth)

        self.archive_v1 = ArchiveV1(self._client, self._gateway_url)
        self.orders_v1 = OrdersV1(self._client, self._gateway_url)

    def _setup_client(self) -> AbstractClient:
        client = self._setup_requests_session()
        if client is None:
            client = UrllibClient()
        return client

    def _setup_requests_session(self) -> Union[AbstractClient, None]:
        try:
            from requests import Session

            from satellitevu.http.requests import RequestsSession
        except ImportError:
            return

        # TODO: Retries
        # TODO: Timeout
        session = Session()
        client = RequestsSession(instance=session)
        return client
