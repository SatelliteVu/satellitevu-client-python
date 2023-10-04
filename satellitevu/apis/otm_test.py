from json import dumps, loads
from urllib.parse import urlparse

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
        ("v2", "otm/v2/contract-id/tasking/feasibilities/", "otm_client"),
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
        == f"{otm_request_parameters['date_from']}/{otm_request_parameters['date_to']}"
    )
