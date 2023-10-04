from json import dumps, loads
from urllib.parse import urlparse
from uuid import uuid4

from mocket import Mocket, mocketize
from mocket.mockhttp import Entry
from pytest import fixture, mark


@fixture()
def versioned_otm_client(request, client):
    if request.getfixturevalue("version") == "v1":
        yield client.future.otm_v1
    else:
        yield client.future.otm_v2


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_otm_client"],
    (
        ("v1", "otm/v1/tasking/feasibilities/", "versioned_otm_client"),
        ("v2", "otm/v2/contract-id/tasking/feasibilities/", "versioned_otm_client"),
    ),
    indirect=["versioned_otm_client"],
)
def test_post_feasibility(
    oauth_token_entry,
    client,
    otm_request_parameters,
    otm_response,
    version,
    api_path,
    versioned_otm_client,
):
    contract_id = otm_request_parameters["contract_id"]
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "POST",
        client._gateway_url + api_path,
        body=dumps(otm_response),
        status=200,
    )

    if version == "v1":
        assert contract_id not in api_path

    response = versioned_otm_client.post_feasibility(**otm_request_parameters)
    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Content-Type"] == "application/json"
    assert api_request.headers["Authorization"] == "Bearer mock-token"

    api_request_body = loads(api_request.body)
    assert api_request_body["geometry"] == {
        "type": "Point",
        "coordinates": otm_request_parameters["coordinates"],
    }
    assert (
        api_request_body["properties"]["max_cloud_cover"]
        == otm_request_parameters["max_cloud_cover"]
    )
    assert (
        api_request_body["properties"]["min_off_nadir"]
        == otm_request_parameters["min_off_nadir"]
    )
    assert (
        api_request_body["properties"]["max_off_nadir"]
        == otm_request_parameters["max_off_nadir"]
    )
    assert (
        api_request_body["properties"]["datetime"]
        == f"{otm_request_parameters['date_from'].isoformat()}/{otm_request_parameters['date_to'].isoformat()}"  # noqa: E501
    )


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_otm_client"],
    (
        ("v1", "otm/v1/tasking/feasibilities/", "versioned_otm_client"),
        ("v2", "otm/v2/contract-id/tasking/feasibilities/", "versioned_otm_client"),
    ),
    indirect=["versioned_otm_client"],
)
def test_get_feasibility(
    oauth_token_entry,
    client,
    otm_request_parameters,
    otm_response,
    version,
    api_path,
    versioned_otm_client,
):
    feasibility_id = uuid4()
    contract_id = otm_request_parameters["contract_id"]
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + api_path + str(feasibility_id),
        status=200,
        body=dumps(otm_response),
    )

    if version == "v1":
        assert contract_id not in api_path
        response = versioned_otm_client.get_feasibility(id=feasibility_id)
    else:
        response = versioned_otm_client.get_feasibility(
            contract_id=contract_id, id=feasibility_id
        )

    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path + f"{feasibility_id}"
    assert api_request.headers["Authorization"] == "Bearer mock-token"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "versioned_otm_client"],
    (
        ("v1", "otm/v1/tasking/feasibilities/", "versioned_otm_client"),
        ("v2", "otm/v2/contract-id/tasking/feasibilities/", "versioned_otm_client"),
    ),
    indirect=["versioned_otm_client"],
)
def test_get_feasibility_response(
    oauth_token_entry,
    client,
    otm_request_parameters,
    otm_response,
    version,
    api_path,
    versioned_otm_client,
):
    feasibility_id = uuid4()
    contract_id = otm_request_parameters["contract_id"]
    api_path = api_path.replace("contract-id", str(contract_id))

    Entry.single_register(
        "GET",
        client._gateway_url + api_path + str(feasibility_id) + "/response",
        status=200,
        body=dumps(otm_response),
    )

    if version == "v1":
        assert contract_id not in api_path
        response = versioned_otm_client.get_feasibility_response(id=feasibility_id)
    else:
        response = versioned_otm_client.get_feasibility_response(
            contract_id=contract_id, id=feasibility_id
        )

    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path + f"{feasibility_id}/response"
    assert api_request.headers["Authorization"] == "Bearer mock-token"


@mocketize(strict_mode=True)
@mark.parametrize(
    ["version", "api_path", "per_page", "versioned_otm_client"],
    (
        (
            "v1",
            "otm/v1/tasking/feasibilities/",
            None,
            "versioned_otm_client",
        ),
        (
            "v1",
            "otm/v1/tasking/feasibilities/",
            10,
            "versioned_otm_client",
        ),
        (
            "v2",
            "otm/v2/contract-id/tasking/feasibilities/",
            None,
            "versioned_otm_client",
        ),
        (
            "v2",
            "otm/v2/contract-id/tasking/feasibilities/",
            10,
            "versioned_otm_client",
        ),
    ),
    indirect=["versioned_otm_client"],
)
def test_list_feasibilities(
    oauth_token_entry,
    client,
    otm_request_parameters,
    otm_response,
    version,
    api_path,
    per_page,
    versioned_otm_client,
):
    contract_id = otm_request_parameters["contract_id"]
    per_page = per_page if not None else 25
    api_path = api_path.replace("contract-id", str(contract_id)) + f"?{per_page=}"

    Entry.single_register(
        "GET",
        client._gateway_url + api_path,
        status=200,
        body=dumps(otm_response),
    )

    if version == "v1":
        assert contract_id not in api_path
        response = versioned_otm_client.list_feasibility_requests(per_page=per_page)
    else:
        response = versioned_otm_client.list_feasibility_requests(
            contract_id=contract_id, per_page=per_page
        )

    assert isinstance(response, dict)

    requests = Mocket.request_list()
    assert len(requests) == 2

    api_request = requests[-1]
    assert api_request.headers["Host"] == urlparse(client._gateway_url).hostname
    assert api_request.path == "/" + api_path
    assert api_request.headers["Authorization"] == "Bearer mock-token"