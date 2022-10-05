from importlib import import_module
from json import dumps
from unittest.mock import Mock

from mocket import Mocketizer
from mocket.mockhttp import Entry
from pytest import fixture, mark, param, skip

from . import ResponseWrapper, UrllibClient

try:
    from requests import Session as RequestsSession
except ImportError:
    RequestsSession = None
try:
    from httpx import Client as HttpxClient
except ImportError:
    HttpxClient = None


@fixture(
    params=(
        param("UrllibClient"),
        param(
            "requests.RequestsSession",
            marks=[
                mark.skipif(RequestsSession is None, reason="requests is not installed")
            ],
        ),
        param(
            "HttpxClient",
            marks=[mark.skipif(HttpxClient is None, reason="httpx is not installed")],
        ),
    )
)
def http_client_class(request):
    full_path = f"{__package__}.{request.param}"
    module = import_module(full_path.rsplit(".", maxsplit=1)[0])
    return getattr(module, full_path.rsplit(".")[-1])


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


def test_http_custom_actor(http_client_class):
    if http_client_class == UrllibClient:
        skip("UrllibClient does not support custom instance")

    instance = Mock()
    client = http_client_class(instance=instance)
    client.request("GET", "http://example.com/")

    assert instance.request.called
