from importlib.metadata import version
from json import dumps
from unittest.mock import Mock

from mocket import Mocket, Mocketizer
from mocket.mockhttp import Entry
from pytest import mark, skip

from satellitevu.auth.auth import Auth

from . import ResponseWrapper, UrllibClient


@mark.parametrize("method", ("GET", "POST"))
def test_http_client(http_client_class, method):
    client = http_client_class()

    Entry.single_register(
        method, "http://example.com/", body=dumps({"message": "Hello"})
    )
    with Mocketizer():
        response = client.request(method, "http://example.com/")

    assert isinstance(response, ResponseWrapper)
    assert response.json() == {"message": "Hello"}


def test_http_client_user_agent(http_client_class):
    client = http_client_class()

    Entry.single_register(
        "GET", "http://example.com/", body=dumps({"message": "Hello"})
    )

    with Mocketizer():
        client.request("GET", "http://example.com/")
        requests = Mocket.request_list()

    sv_version = version("satellitevu")
    sv_comment = f"(satellitevu/{sv_version})"
    assert requests[0].headers.get("user-agent").endswith(sv_comment)


def test_http_custom_actor(http_client_class):
    if http_client_class == UrllibClient:
        skip("UrllibClient does not support custom instance")

    instance = Mock()
    client = http_client_class(instance=instance)
    client.request("GET", "http://example.com/")

    assert instance.request.called


@mark.parametrize(
    "url, headers, uses_injected_auth",
    (
        ("http://example.com/", None, False),
        ("http://api.example.com/", None, False),
        ("http://api.example.com/non-authed", None, False),
        ("http://api.example.com/authed/", None, True),
        ("http://api.example.com/authed/subpath", None, True),
        (
            "http://api.example.com/authed/subpath",
            {"authorization": "some-other"},
            False,
        ),
    ),
)
def test_http_set_auth(http_client_class, url, headers, uses_injected_auth):
    auth = Mock(wraps=Auth(client_id="mocked", client_secret="mocked"))
    auth.token.return_value = "mock-token"
    Entry.single_register("GET", url)

    client = http_client_class()
    client.set_auth("http://api.example.com/authed/", auth)

    with Mocketizer():
        client.request("GET", url, headers=headers)
        requests = Mocket.request_list()

    assert len(requests) == 1
    assert (
        requests[0].headers.get("authorization") == "Bearer mock-token"
    ) == uses_injected_auth


@mark.parametrize(
    "data, json, body, content_type",
    (
        ({"foo": "bar"}, None, "foo=bar", "application/x-www-form-urlencoded"),
        (None, {"foo": "bar"}, '{"foo": "bar"}', "application/json"),
        (
            {"bar": "foo"},
            {"foo": "bar"},
            "bar=foo",
            "application/x-www-form-urlencoded",
        ),
    ),
)
def test_payload(http_client_class, data, json, body, content_type):
    client = http_client_class()
    Entry.single_register("POST", "http://api.example.com")

    with Mocketizer():
        client.request("POST", "http://api.example.com", data=data, json=json)
        request = Mocket.last_request()
    assert request.headers["content-type"] == content_type
    assert request.body == body
