from typing import Dict, Optional, Union
from warnings import warn

from satellitevu.apis.id import IdV2
from satellitevu.apis.archive import ArchiveV2
from satellitevu.apis.catalog import CatalogV1
from satellitevu.apis.contracts import ContractsV1
from satellitevu.apis.orders import OrdersV2
from satellitevu.apis.otm import OtmV2
from satellitevu.auth import AbstractCache, Auth
from satellitevu.config import GATEWAY
from satellitevu.http import AbstractClient, UrllibClient


class FutureApis:
    _called: Dict[str, bool] = {}

    def __init__(self, client: AbstractClient, gateway_url: str):
        pass

    def __getattribute__(self, __name: str):
        attr = super().__getattribute__(__name)
        if __name != "_called":
            has_been_called = self._called.get(__name, False)
            self._called[__name] = True
            if not has_been_called:
                warn(
                    f"{__name} is a not yet a stable API. Use at own risk",
                    FutureWarning,
                )
        return attr


class Client:
    _client: AbstractClient
    _gateway_url: str

    auth: Auth

    contracts_v1: ContractsV1

    archive_v2: ArchiveV2
    catalog_v1: CatalogV1
    id_v2: IdV2
    orders_v2: OrdersV2
    otm_v2: OtmV2

    future: FutureApis

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

        self.contracts_v1 = ContractsV1(
            client=self._client, base_url=self._gateway_url, auth=self.auth
        )

        self.archive_v2 = ArchiveV2(self._client, self._gateway_url)
        self.catalog_v1 = CatalogV1(self._client, self._gateway_url)
        self.id_v2 = IdV2(self._client, self._gateway_url)
        self.orders_v2 = OrdersV2(self._client, self._gateway_url)
        self.otm_v2 = OtmV2(self._client, self._gateway_url)

        self.future = FutureApis(self._client, self._gateway_url)

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
