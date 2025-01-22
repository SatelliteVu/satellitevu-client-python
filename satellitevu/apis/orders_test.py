from allure import description, story, title
import tempfile
from io import BytesIO
from json import dumps
from unittest.mock import patch
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import pytest
from mocket import Mocket
from mocket.mockhttp import Entry, Response
from pytest import mark

from satellitevu.apis.orders import bytes_to_file
from satellitevu.auth.exc import Api401Error, Api403Error

API_PATH = "orders/v2/contract-id/"


@mark.usefixtures("mocketize_fixture")
@story("Orders")
class TestOrders:
    @title("Submit order (single item)")
    @description("Submit an order for a single item")
    @mark.parametrize("pact", ["cos"], indirect=True)
    @mark.parametrize(
        "item_ids",
        (
            ("20221005T214049000_basic_0_TABI"),
            ("20220923T222227000_basic_0_TABI"),
        ),
    )
    def test_submit_single_item(self, client, oauth_token_entry, item_ids, pact):
        payload = dumps({"item_id": [item_ids]})
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            body=dumps(payload),
            status=201,
        )

        response = client.orders_v2.submit(contract_id=contract_id, item_ids=item_ids)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}"
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry
        assert api_request.body == payload

        assert response.status == 201
        cos_response_body = dumps(
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                        "properties": {
                            "item_id": "20220923T222227000_basic_0_TABI",
                            "order_id": "1cfdc8cc-968d-406c-bada-d45c55a26857",
                            "created_at": "2019-08-24T14:15:22Z",
                            "stac_metadata": {
                                "id": "string",
                                "collection": "string",
                                "assets": {
                                    "property1": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                    "property2": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                },
                                "bbox": [0, 0, 0, 0],
                                "properties": {
                                    "eo:cloud_cover": 0,
                                    "datetime": "2019-08-24T14:15:22Z",
                                    "gsd": 0,
                                    "platform": "string",
                                    "view:azimuth": 0,
                                    "view:off_nadir": 0,
                                    "view:sun_azimuth": 0,
                                    "view:sun_elevation": 0,
                                },
                            },
                            "price": {"value": 100000, "currency": "GBP"},
                        },
                    }
                ],
                "owned_by": "John Doe",
                "created_at": "2019-08-24T14:15:22Z",
                "updated_at": "2019-08-24T14:15:22Z",
                "contract_id": "9aafc1a8-e497-46c9-ba0b-bd5b03c353e4",
                "price": {"value": 100000, "currency": "GBP"},
            }
        )

        (
            pact.upon_receiving("An order for a single item")
            .given("contract has credit")
            .with_request(method="POST", path=f"/{contract_id}/")
            .with_body(payload)
            .will_respond_with(201)
            .with_body(cos_response_body)
        )

    @title("Submit order (multiple items)")
    @description("Submit an order for a single item")
    @mark.parametrize("pact", ["cos"], indirect=True)
    @mark.parametrize(
        "item_ids",
        (
            (["20221005T214049000_basic_0_TABI", "20220923T222227000_basic_0_TABI"]),
            (["20220923T222227000_basic_0_TABI"]),
        ),
    )
    def test_submit_multiple_items(self, client, oauth_token_entry, item_ids, pact):
        payload = dumps({"item_id": item_ids})
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            body=dumps(payload),
            status=201,
        )

        response = client.orders_v2.submit(contract_id=contract_id, item_ids=item_ids)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}"
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry
        assert api_request.body == payload

        assert response.status == 201

        cos_response_body = dumps(
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                        "properties": {
                            "item_id": "20221005T214049000_basic_0_TABI",
                            "order_id": "1cfdc8cc-968d-406c-bada-d45c55a26857",
                            "created_at": "2019-08-24T14:15:22Z",
                            "stac_metadata": {
                                "id": "string",
                                "collection": "string",
                                "assets": {
                                    "property1": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                    "property2": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                },
                                "bbox": [0, 0, 0, 0],
                                "properties": {
                                    "eo:cloud_cover": 0,
                                    "datetime": "2019-08-24T14:15:22Z",
                                    "gsd": 0,
                                    "platform": "string",
                                    "view:azimuth": 0,
                                    "view:off_nadir": 0,
                                    "view:sun_azimuth": 0,
                                    "view:sun_elevation": 0,
                                },
                            },
                            "price": {"value": 100000, "currency": "GBP"},
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                        "properties": {
                            "item_id": "20220923T222227000_basic_0_TABI",
                            "order_id": "1cfdc8cc-968d-406c-bada-d45c55a26857",
                            "created_at": "2019-08-24T14:15:22Z",
                            "stac_metadata": {
                                "id": "string",
                                "collection": "string",
                                "assets": {
                                    "property1": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                    "property2": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                },
                                "bbox": [0, 0, 0, 0],
                                "properties": {
                                    "eo:cloud_cover": 0,
                                    "datetime": "2019-08-24T14:15:22Z",
                                    "gsd": 0,
                                    "platform": "string",
                                    "view:azimuth": 0,
                                    "view:off_nadir": 0,
                                    "view:sun_azimuth": 0,
                                    "view:sun_elevation": 0,
                                },
                            },
                            "price": {"value": 100000, "currency": "GBP"},
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                        "properties": {
                            "item_id": "20220923T222227000_basic_0_TABI",
                            "order_id": "1cfdc8cc-968d-406c-bada-d45c55a26857",
                            "created_at": "2019-08-24T14:15:22Z",
                            "stac_metadata": {
                                "id": "string",
                                "collection": "string",
                                "assets": {
                                    "property1": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                    "property2": {
                                        "href": "http://example.com",
                                        "type": "string",
                                        "roles": ["string"],
                                    },
                                },
                                "bbox": [0, 0, 0, 0],
                                "properties": {
                                    "eo:cloud_cover": 0,
                                    "datetime": "2019-08-24T14:15:22Z",
                                    "gsd": 0,
                                    "platform": "string",
                                    "view:azimuth": 0,
                                    "view:off_nadir": 0,
                                    "view:sun_azimuth": 0,
                                    "view:sun_elevation": 0,
                                },
                            },
                            "price": {"value": 100000, "currency": "GBP"},
                        },
                    },
                ],
                "owned_by": "John Doe",
                "created_at": "2019-08-24T14:15:22Z",
                "updated_at": "2019-08-24T14:15:22Z",
                "contract_id": "9aafc1a8-e497-46c9-ba0b-bd5b03c353e4",
                "price": {"value": 100000, "currency": "GBP"},
            }
        )

        (
            pact.upon_receiving("An order for multiple items")
            .given("contract has credit")
            .with_request(method="POST", path=f"/{contract_id}/")
            .with_body(payload)
            .will_respond_with(201)
            .with_body(cos_response_body)
        )

    @title("Get order download URL")
    @description("Download order URL")
    def test_item_download_url(self, client, oauth_token_entry, redirect_response):
        order_id = str(uuid4())
        item_id = "20221005T214049000_basic_0_TABI"
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url
            + f"{api_path}{order_id}/{item_id}/download?redirect=False",
            body=dumps(redirect_response),
        )

        response = client.orders_v2.item_download_url(
            contract_id=contract_id, order_id=order_id, item_id=item_id
        )

        requests = Mocket.request_list()

        assert len(requests) == 2
        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert (
            api_request.path
            == f"/{api_path}{order_id}/{item_id}/download?redirect=False"
        )
        assert api_request.headers["authorization"] == oauth_token_entry

        assert isinstance(response, dict)
        assert response["url"] == "https://image.test"

    @title("Download an order (unauthorized")
    @description("Attempt to download an order without authorization")
    @mark.parametrize(
        ["status", "exception"],
        (
            (401, Api401Error),
            (403, Api403Error),
        ),
    )
    def test_no_access_to_download_if_unauthorized(
        self, client, oauth_token_entry, status, exception, redirect_response
    ):
        order_id = str(uuid4())
        item_id = "20231110T173102000_visual_30_hotsat"
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url
            + f"{api_path}{order_id}/{item_id}/download?redirect=False",
            body=dumps(redirect_response),
            status=status,
        )

        with pytest.raises(exception):
            client.orders_v2.item_download_url(
                contract_id=contract_id, order_id=order_id, item_id=item_id
            )

        requests = Mocket.request_list()

        assert len(requests) == 2
        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert (
            api_request.path
            == f"/{api_path}{order_id}/{item_id}/download?redirect=False"
        )
        assert api_request.headers["authorization"] == oauth_token_entry

    @title("Download order item")
    @description("Download an order")
    @mark.parametrize("pact", ["cos"], indirect=True)
    def test_download_order_item(
        self, client, oauth_token_entry, redirect_response, pact
    ):
        order_id = str(uuid4())
        item_id = "20231110T173102000_visual_30_hotsat"
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))
        download_dir = "downloads"

        Entry.register(
            "GET",
            client._gateway_url
            + f"{api_path}{order_id}/{item_id}/download?redirect=False",
            Response(headers={"Retry-After": "1"}, status=202),
            Response(body=dumps(redirect_response), status=200),
        )
        Entry.single_register("GET", uri=redirect_response["url"])

        with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
            mock_file_dl.return_value = f"{download_dir}/image.zip"

            response = client.orders_v2.download_item(
                contract_id=contract_id,
                order_id=order_id,
                item_id=item_id,
                destdir=download_dir,
            )

        requests = Mocket.request_list()

        assert len(requests) == 4

        api_request = requests[2]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert (
            api_request.path
            == f"/{api_path}{order_id}/{item_id}/download?redirect=False"
        )
        assert api_request.headers["authorization"] == oauth_token_entry

        mock_file_dl.assert_called_once()
        assert response == mock_file_dl()
        assert isinstance(response, str)

        Mocket.assert_fail_if_entries_not_served()

        (
            pact.upon_receiving("A Request to download an order item")
            .given("contract has credit")
            .with_request(
                method="GET", path=f"/{contract_id}/{order_id}/{item_id}/download"
            )
            .with_query_parameter("redirect", "false")
            .will_respond_with(200)
            .with_body(redirect_response)
        )

    @title("Get order details")
    @description("Get the details of an existing order")
    @mark.parametrize("pact", ["cos"], indirect=True)
    def test_get_order_details(
        self, client, oauth_token_entry, order_details_response, pact
    ):
        contract_id = str(uuid4())
        order_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url + f"{api_path}{order_id}",
            body=dumps(order_details_response),
        )

        response = client.orders_v2.get_order_details(
            contract_id=contract_id, order_id=order_id
        )

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}{order_id}"
        assert api_request.headers["authorization"] == oauth_token_entry

        assert isinstance(response, dict)

        (
            pact.upon_receiving("Details for an existing order")
            .given("order exists")
            .with_request(method="GET", path=f"/{contract_id}/{order_id}/")
            .will_respond_with(200)
            .with_body(order_details_response)
        )

    @title("Get orders")
    @description("Get a list of orders")
    @mark.parametrize("pact", ["cos"], indirect=True)
    def test_get_orders(self, client, oauth_token_entry, order_list_response, pact):
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            body=dumps(order_list_response),
        )

        response = client.orders_v2.get_orders(contract_id=contract_id)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}"
        assert api_request.headers["authorization"] == oauth_token_entry

        assert isinstance(response, dict)

        (
            pact.upon_receiving("Get list of orders")
            .given("order exists")
            .with_request(method="GET", path=f"/{contract_id}/")
            .will_respond_with(200)
            .with_body(order_list_response)
        )

    @title("Get order details (unauthorized)")
    @description("Attempt to get order details without authorization")
    @mark.parametrize(
        ["status", "exception"],
        (
            (401, Api401Error),
            (403, Api403Error),
        ),
    )
    def test_cannot_get_order_details_if_unauthorized(
        self, client, oauth_token_entry, status, exception, order_details_response
    ):
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        order_id = str(uuid4())

        Entry.single_register(
            "GET",
            client._gateway_url + f"{api_path}{order_id}",
            body=dumps(order_details_response),
            status=status,
        )

        with pytest.raises(exception):
            client.orders_v2.get_order_details(
                contract_id=contract_id, order_id=order_id
            )

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}{order_id}"
        assert api_request.headers["authorization"] == oauth_token_entry

    @title("Download order")
    @description("Download an order")
    def test_download_order(
        self,
        client,
        oauth_token_entry,
        redirect_response,
    ):
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))
        order_id = "528b0f77-5df1-4ed7-9224-502817170613"
        download_dir = "downloads"

        Entry.register(
            "GET",
            client._gateway_url + f"{api_path}{order_id}/download?redirect=False",
            Response(headers={"Retry-After": "1"}, status=202),
            Response(body=dumps(redirect_response), status=200),
        )
        Entry.single_register("GET", uri=redirect_response["url"])

        with patch("satellitevu.apis.orders.bytes_to_file") as mock_file_dl:
            mock_file_dl.return_value = f"{download_dir}/{order_id}.zip"

            response = client.orders_v2.download_order(
                contract_id=contract_id, order_id=order_id, destdir=download_dir
            )

        requests = Mocket.request_list()

        assert len(requests) == 4

        api_request = requests[1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}{order_id}/download?redirect=False"
        assert api_request.headers["authorization"] == oauth_token_entry

        mock_file_dl.assert_called_once()
        assert response == mock_file_dl()
        assert isinstance(response, str)

        Mocket.assert_fail_if_entries_not_served()

    @mark.parametrize(
        ["status", "exception"],
        (
            (401, Api401Error),
            (403, Api403Error),
        ),
    )
    @title("Download an order (unauthorized)")
    @description("Attempt to download an order without authorization")
    def test_download_order_unauthorized(
        self,
        client,
        redirect_response,
        status,
        exception,
    ):
        contract_id = str(uuid4())
        api_path = API_PATH.replace("contract-id", str(contract_id))

        order_id = "528b0f77-5df1-4ed7-9224-502817170613"
        download_dir = "downloads"

        Entry.single_register(
            "POST",
            urljoin(client.auth.auth_url, "oauth/token"),
            body=dumps({"access_token": None}),
        )

        Entry.single_register(
            "GET",
            client._gateway_url + f"{api_path}{order_id}/download?redirect=False",
            body=dumps(redirect_response),
            status=status,
        )

        with pytest.raises(exception):
            client.orders_v2.download_order(
                contract_id=contract_id, order_id=order_id, destdir=download_dir
            )

        requests = Mocket.request_list()

        assert len(requests) == 2

        api_request = requests[1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == f"/{api_path}{order_id}/download?redirect=False"
        assert api_request.headers["authorization"] == "Bearer None"

    @title("Write bytes to file")
    @description("Write bytes to a file")
    def test_bytes_to_file(self):
        outfile_path = tempfile.mkstemp()[1]
        output = bytes_to_file(BytesIO(b"Hello world"), outfile_path)

        assert isinstance(output, str)
