from allure import description, title, suite
from json import dumps, loads
from itertools import product
from secrets import token_urlsafe
from unittest.mock import patch
from urllib.parse import urlparse
from uuid import uuid4

from mocket import Mocket
from mocket.mockhttp import Entry, Response
from pytest import mark, raises

from satellitevu.apis.exceptions import OTMOrderCancellationError, OTMParametersError

API_PATH_FEASIBILITY = "otm/v2/contract-id/tasking/feasibilities/"
API_PATH_ORDERS = "otm/v2/contract-id/tasking/orders/"


@suite("Tasking")
@mark.usefixtures("mocketize_fixture")
class TestTasking:
    @title("Cannot use OTM v2 without contract ID")
    @description("Ensure that OTM v2 methods cannot be used without a contract ID")
    def test_cannot_use_v2_without_contract_id(self, client):
        error_message = "missing 1 required keyword-only argument: 'contract_id'"
        with raises(TypeError) as exc:
            client.otm_v2.get_order(order_id=uuid4())

        assert error_message in str(exc.value)

    @title("Feasibility POST request")
    @description("Test the POST request for feasibility")
    @mark.parametrize("product", ("standard", "assured"))
    def test_post_feasibility(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_response,
        product,
    ):
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_FEASIBILITY.replace("contract-id", str(contract_id))

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            body=dumps(otm_response),
            status=202,
        )

        response = client.otm_v2.post_feasibility(
            **otm_request_parameters,
            product=product,
        )
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        api_request_body = loads(api_request.body)
        assert api_request_body["geometry"] == {
            "type": "Point",
            "coordinates": otm_request_parameters["coordinates"],
        }

        properties_keys = ["max_cloud_cover", "min_off_nadir", "max_off_nadir"]

        if product == "assured":
            for key in properties_keys:
                assert not api_request_body["properties"].get(key)
        elif product == "standard":
            for key in properties_keys:
                assert (
                    api_request_body["properties"][key] == otm_request_parameters[key]
                )

        assert (
            api_request_body["properties"]["datetime"]
            == f"{otm_request_parameters['date_from'].isoformat()}/{otm_request_parameters['date_to'].isoformat()}"  # noqa: E501
        )

    @title("Create a feasibility request")
    @description("Test the POST request for feasibility with off-nadir and GSD values")
    @mark.parametrize("product", ("standard", "assured"))
    def test_post_feasibility_off_nadir_gsd_values(
        self, oauth_token_entry, client, otm_request_parameters, product, otm_response
    ):
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_FEASIBILITY.replace("contract-id", str(contract_id))

        otm_request_parameters["product"] = product
        for param in ["min_off_nadir", "max_off_nadir", "min_gsd", "max_gsd"]:
            otm_request_parameters[param] = None

        if product == "assured":
            Entry.single_register(
                "POST",
                client._gateway_url + api_path,
                body=dumps(otm_response),
                status=202,
            )

            response = client.otm_v2.post_feasibility(
                **otm_request_parameters,
            )
            assert isinstance(response, dict)

        else:
            with raises(OTMParametersError):
                client.otm_v2.post_feasibility(**otm_request_parameters)

    @title("Feasibility GET request")
    @description("Get details about a feasibility request")
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_get_feasibility(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_feasibility_body,
        pact,
    ):
        feasibility_id = uuid4()
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_FEASIBILITY.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url + api_path + str(feasibility_id),
            status=200,
            body=dumps(otm_feasibility_body),
        )

        response = client.otm_v2.get_feasibility(
            contract_id=contract_id, id=feasibility_id
        )

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path + f"{feasibility_id}"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Retrieve details of a feasibility request")
            .given("the feasibility request exists")
            .with_request(
                method="GET",
                path=f"/{contract_id}/tasking/feasibilities/{feasibility_id}",
            )
            .will_respond_with(200)
            .with_body(otm_feasibility_body)
        )

    @title("Get feasibility response")
    @description("Test the GET request for feasibility response")
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_get_feasibility_response(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_feasibility_response_body,
        pact,
    ):
        feasibility_id = uuid4()
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_FEASIBILITY.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url + api_path + str(feasibility_id) + "/response",
            status=200,
            body=dumps(otm_feasibility_response_body),
        )

        response = client.otm_v2.get_feasibility_response(
            contract_id=contract_id, id=feasibility_id
        )

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path + f"{feasibility_id}/response"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Retrieve details of a feasibility request response")
            .given("the feasibility request exists")
            .with_request(
                method="GET",
                path=f"/{contract_id}/tasking/feasibilities/{feasibility_id}/response",
            )
            .will_respond_with(200)
            .with_body(otm_feasibility_response_body)
        )

    @title("List feasibilities")
    @description("Test the GET request for listing feasibilities")
    @mark.parametrize(
        "per_page",
        (None, 10),
    )
    def test_list_feasibilities(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_response,
        per_page,
    ):
        contract_id = otm_request_parameters["contract_id"]
        per_page = per_page if not None else 25
        api_path = (
            API_PATH_FEASIBILITY.replace("contract-id", str(contract_id))
            + f"?{per_page=}"
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=dumps(otm_response),
        )

        response = client.otm_v2.list_feasibility_requests(
            contract_id=contract_id, per_page=per_page
        )

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

    @title("Create a tasking order")
    @description("Test the POST request for creating a tasking order")
    @mark.parametrize("product", ("standard", "assured"))
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_post_order(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_order_confirmation,
        product,
        pact,
    ):
        contract_id = otm_request_parameters["contract_id"]
        otm_request_parameters["extra_kwarg"] = "extra_kwarg_value"
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))

        if product == "assured":
            otm_request_parameters["product"] = product
            otm_request_parameters["signature"] = token_urlsafe(16)

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            body=dumps(otm_order_confirmation),
            status=201,
        )

        response = client.otm_v2.create_order(**otm_request_parameters)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        api_request_body = loads(api_request.body)
        print(api_request_body)
        properties_keys = ["max_cloud_cover", "min_off_nadir", "max_off_nadir"]

        if product == "assured":
            assert "geometry" not in api_request_body.keys()
            assert "signature" in api_request_body["properties"].keys()
            for key in properties_keys:
                assert not api_request_body["properties"].get(key)
            assert api_request_body["properties"]["extra_kwarg"] == "extra_kwarg_value"
        else:
            assert api_request_body["geometry"] == {
                "type": "Point",
                "coordinates": otm_request_parameters["coordinates"],
            }
            assert "signature" not in api_request_body["properties"].keys()
            for key in properties_keys:
                assert (
                    api_request_body["properties"][key] == otm_request_parameters[key]
                )
            assert (
                api_request_body["properties"]["datetime"]
                == f"{otm_request_parameters['date_from'].isoformat()}/{otm_request_parameters['date_to'].isoformat()}"  # noqa: E501
            )
            assert api_request_body["properties"]["extra_kwarg"] == "extra_kwarg_value"

            (
                pact.upon_receiving(f"A tasking order ({product})")
                .given("contract has credit")
                .with_request(method="POST", path=f"/{contract_id}/tasking/orders")
                .with_body(api_request_body)
                .will_respond_with(201)
                .with_body(otm_order_confirmation)
            )

    @title("Create a tasking order")
    @mark.parametrize("product", ("standard", "assured"))
    def test_create_order_off_nadir_gsd_values(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        product,
        otm_response,
    ):
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))

        otm_request_parameters["product"] = product
        otm_request_parameters["signature"] = token_urlsafe(16)
        for param in ["min_off_nadir", "max_off_nadir", "min_gsd", "max_gsd"]:
            otm_request_parameters[param] = None

        if product == "assured":
            Entry.single_register(
                "POST",
                client._gateway_url + api_path,
                body=dumps(otm_response),
                status=201,
            )

            response = client.otm_v2.create_order(**otm_request_parameters)
            assert isinstance(response, dict)
        else:
            with raises(OTMParametersError):
                client.otm_v2.create_order(**otm_request_parameters)

    @title("Create a tasking order with addons")
    @description("Test the POST request for creating a tasking order with addons")
    @mark.parametrize(
        "product, withhold",
        product(
            ("standard", "assured"),
            (
                "0d",
                "7d",
                "1y",
            ),
        ),
    )
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_create_order_with_addons(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        product,
        withhold,
        otm_order_confirmation,
        pact,
    ):
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))

        otm_request_parameters["product"] = product
        otm_request_parameters["signature"] = token_urlsafe(16)
        otm_request_parameters["addon_withhold"] = withhold

        if product == "assured":
            Entry.single_register(
                "POST",
                client._gateway_url + api_path,
                body=dumps(otm_order_confirmation),
                status=201,
            )

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            body=dumps(otm_order_confirmation),
            status=201,
        )

        response = client.otm_v2.create_order(**otm_request_parameters)
        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["content-type"] == "application/json"
        assert api_request.headers["authorization"] == oauth_token_entry

        api_request_body = loads(api_request.body)

        assert api_request_body["properties"]["product"] == product

        if withhold:
            assert api_request_body["properties"]["addon:withhold"] == withhold
        else:
            assert "addon:withhold" not in api_request_body["properties"].keys()

        (
            pact.upon_receiving(f"A tasking order with addons ({product})")
            .given("contract has credit")
            .with_request(method="POST", path=f"/{contract_id}/tasking/orders")
            .with_body(api_request_body)
            .will_respond_with(201)
            .with_body(otm_order_confirmation)
        )

    @title("Create a tasking order without signature")
    @description(
        "Test the POST request for creating a tasking order without a signature"
    )
    def test_post_assured_order_without_signature(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_response,
    ):
        otm_request_parameters["product"] = "assured"

        with raises(
            Exception,
            match="Orders with assured priority must have a signature token.",
        ):
            client.otm_v2.create_order(**otm_request_parameters)

    @title("List tasking orders")
    @description("Retrieve a list of tasking orders")
    @mark.parametrize(
        "per_page",
        (None, 10),
    )
    def test_list_tasking_orders(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_response,
        per_page,
    ):
        contract_id = otm_request_parameters["contract_id"]
        per_page = per_page if not None else 25
        api_path = (
            API_PATH_ORDERS.replace("contract-id", str(contract_id)) + f"?{per_page=}"
        )

        Entry.single_register(
            "GET",
            client._gateway_url + api_path,
            status=200,
            body=dumps(otm_response),
        )

        response = client.otm_v2.list_orders(contract_id=contract_id, per_page=per_page)

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

    @title("Get tasking order")
    @description("Retrieve a specific tasking order")
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_get_tasking_order(
        self,
        oauth_token_entry,
        client,
        otm_request_parameters,
        otm_order_response,
        pact,
    ):
        order_id = uuid4()
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))

        Entry.single_register(
            "GET",
            client._gateway_url + api_path + str(order_id),
            status=200,
            body=dumps(otm_order_response),
        )

        response = client.otm_v2.get_order(contract_id=contract_id, order_id=order_id)

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path + f"{order_id}"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Retrieve details of a tasking order")
            .given("the order exists")
            .with_request(
                method="GET", path=f"/{contract_id}/tasking/orders/{order_id}"
            )
            .will_respond_with(200)
            .with_body(otm_order_response)
        )

    @title("Cancel tasking order")
    @description("Cancel a specific tasking order")
    @mark.parametrize("status_code", (204, 404, 409))
    @mark.parametrize("pact", ["otm"], indirect=True)
    def test_cancel_tasking_order(
        self, oauth_token_entry, client, otm_request_parameters, status_code, pact
    ):
        order_id = uuid4()
        contract_id = otm_request_parameters["contract_id"]
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))

        Entry.single_register(
            "POST",
            client._gateway_url + api_path + str(order_id) + "/cancel",
            status=status_code,
        )

        if status_code == 204:
            response = client.otm_v2.cancel_order(
                contract_id=contract_id, order_id=order_id
            )
            assert not response
        else:
            with raises(OTMOrderCancellationError):
                client.otm_v2.cancel_order(contract_id=contract_id, order_id=order_id)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path + f"{order_id}" + "/cancel"
        assert api_request.headers["authorization"] == oauth_token_entry

        (
            pact.upon_receiving("Cancel a tasking order")
            .given("the order exists")
            .with_request(
                method="POST", path=f"/{contract_id}/tasking/orders/{order_id}/cancel"
            )
            .will_respond_with(204)
        )

    @title("Search for tasking orders")
    @description("Search for tasking orders")
    def test_post_search(
        self, oauth_token_entry, client, otm_request_parameters, search_response
    ):
        contract_id = otm_request_parameters["contract_id"]
        api_path = "otm/v2/contract-id/search/".replace("contract-id", str(contract_id))

        Entry.single_register(
            "POST",
            client._gateway_url + api_path,
            status=200,
            body=dumps(search_response),
        )

        search_parameters = {
            "per_page": 100,
            "collections": ["feasibility"],
            "date_range": "2023-01-01T00:00:00/2023-01-31T11:59:59",
            "properties": {"min_gsd": 15, "max_gsd": 35, "status": "feasible"},
            "intersects": {},
            "sort_by": [{"field": "min_gsd", "direction": "asc"}],
        }

        response = client.otm_v2.search(contract_id=contract_id, **search_parameters)

        assert isinstance(response, dict)

        requests = Mocket.request_list()
        assert len(requests) == 2

        api_request = requests[-1]
        assert api_request.headers["host"] == urlparse(client._gateway_url).hostname
        assert api_request.path == "/" + api_path
        assert api_request.headers["authorization"] == oauth_token_entry

    @title("Download tasking order")
    @description("Download a specific tasking order")
    def test_download_order(
        self,
        client,
        oauth_token_entry,
        redirect_response,
    ):
        contract_id = str(uuid4())
        api_path = API_PATH_ORDERS.replace("contract-id", str(contract_id))
        order_id = "528b0f77-5df1-4ed7-9224-502817170613"
        download_dir = "downloads"

        Entry.register(
            "GET",
            client._gateway_url + f"{api_path}{order_id}/download?redirect=False",
            Response(headers={"Retry-After": "1"}, status=202),
            Response(body=dumps(redirect_response), status=200),
        )
        Entry.single_register("GET", uri=redirect_response["url"])

        with patch("satellitevu.apis.otm.bytes_to_file") as mock_file_dl:
            mock_file_dl.return_value = f"{download_dir}/{order_id}.zip"

            response = client.otm_v2.download_order(
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
