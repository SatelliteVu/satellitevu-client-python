from json import dumps
from typing import List
from urllib.parse import parse_qs

from mocket import Mocket, Mocketizer
from mocket.mockhttp import Entry, Request
from pytest import mark

from satellitevu.apis.base import AbstractApi
from satellitevu.auth import Auth
from satellitevu.http.base import AbstractClient


class TestApi(AbstractApi):
    __test__ = False

    api_path = "/test"
    scopes = ["test"]


@mark.parametrize("kwargs", ({}, {"scopes": ["foo"]}))
def test_scopes(kwargs, http_client_class, memory_cache):
    client: AbstractClient = http_client_class()
    auth = Auth(
        client_id="test",
        client_secret="test",  # pragma: allowlist secret
        auth_url="http://auth.example.com",
        cache=memory_cache,
    )
    client.set_auth("http://api.example.com", auth)
    api = TestApi(client, "http://api.example.com")

    Entry.single_register(
        "POST",
        "http://auth.example.com/oauth/token",
        body=dumps({"access_token": "mock-token"}),
    )
    Entry.single_register("GET", api.url("/"), body="")
    with Mocketizer():
        api.make_request("GET", api.url("/"), **kwargs)
        requests: List[Request] = Mocket.request_list()

    assert len(requests) == 2
    assert parse_qs(requests[0].body)["scope"] == kwargs.get("scopes", api.scopes)
