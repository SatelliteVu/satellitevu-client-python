from allure import description, title, suite
from json import dumps
from typing import List
from urllib.parse import parse_qs

from mocket import Mocket, Mocketizer
from mocket.mockhttp import Entry, Request
from pytest import mark, raises, fail

from satellitevu.apis.base import AbstractApi
from satellitevu.auth import Auth
from satellitevu.auth.exc import Api401Error, Api403Error, ApiClientError, ApiServerError
from satellitevu.http.base import AbstractClient, ResponseWrapper


class StubResponseWrapper(ResponseWrapper):
    def __init__(self, raw, headers, status, text):
        self.raw = raw
        self.headers = headers
        self.status = status
        self.text = text

    @classmethod
    def with_error_status(cls, status: int, text: str) -> "StubResponseWrapper":
        return cls(text, {}, status, text)

    def json(self):
        return {}


class StubClient(AbstractClient):
    def __init__(self, response: StubResponseWrapper) -> None:
        self.response = response

    def request(
        self,
        method: str,
        url: str,
        *,
        scopes = None,
        headers = None,
        data = None,
        json = None,
    ) -> StubResponseWrapper:
        return self.response

    @property
    def user_agent(self):
        return ""

    @classmethod
    def with_error_response(cls, status: int, text: str) -> "StubClient":
        return cls(
            StubResponseWrapper.with_error_status(status, text)
        )


class StubApi(AbstractApi):
    __test__ = False

    api_path = "/test"
    scopes = ["test"]


@suite("Base")
class TestAPI:
    @title("Scopes")
    @description("Test that the correct scopes are sent in the request")
    @mark.parametrize("kwargs", ({}, {"scopes": ["foo"]}))
    def test_scopes(self, kwargs, http_client_class, memory_cache):
        client: AbstractClient = http_client_class()
        auth = Auth(
            client_id="test",
            client_secret="test",  # pragma: allowlist secret
            auth_url="http://auth.example.com",
            cache=memory_cache,
        )
        client.set_auth("http://api.example.com", auth)
        api = StubApi(client, "http://api.example.com")

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

    def test_should_raise_401_error_for_401_response(self):
        client = StubClient.with_error_response(401, "No way Jose")

        with raises(Api401Error) as exc_info:
            StubApi(client, "").make_request("POST", "")

        assert exc_info.value.response_status == 401

    def test_should_raise_403_error_for_403_response(self):
        client = StubClient.with_error_response(403, "Can't do that Dave")

        with raises(Api403Error) as exc_info:
            StubApi(client, "").make_request("POST", "")

        assert exc_info.value.response_status == 403

    @mark.parametrize(
            ["status"],
            [
                [400],
                [402],
                [404],
                [499],
            ]
        )
    def test_should_raise_client_error_for_other_4xx_response(self, status):
        client = StubClient.with_error_response(status, "Oh no")

        with raises(ApiClientError) as exc_info:
            StubApi(client, "").make_request("POST", "")

        assert exc_info.value.response_status == status

    @mark.parametrize(
            ["status"],
            [
                [500],
                [501],
                [504],
                [599],
            ]
        )
    def test_should_raise_server_error_for_5xx_response(self, status):
        client = StubClient.with_error_response(status, "Oh no")

        with raises(ApiServerError) as exc_info:
            StubApi(client, "").make_request("POST", "")

        assert exc_info.value.response_status == status

    @mark.parametrize(
            ["status"],
            [
                [100],
                [200],
                [202],
                [301],
            ]
        )
    def test_should_not_raise_error_for_1xx_2xx_response(self, status):
        client = StubClient.with_error_response(status, "Okay!")

        try:
            StubApi(client, "").make_request("POST", "")
        except Exception as e:
            fail(f"Raised error unexpectedly: {e}")

    def test_should_raise_client_error_with_relevant_error_code_and_message(self):
        client = StubClient.with_error_response(422, "Oh no")

        with raises(ApiClientError) as exc_info:
            StubApi(client, "").make_request("POST", "")