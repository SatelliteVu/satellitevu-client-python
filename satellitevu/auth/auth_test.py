from base64 import urlsafe_b64encode
from datetime import datetime
from json import dumps
from socket import error
from typing import Dict
from urllib.error import URLError
from urllib.parse import urljoin

from mocket import mocketize
from mocket.mockhttp import Entry
from pytest import mark, raises

from .auth import Auth, is_expired_token
from .exc import AuthError


def _encode(claims: Dict[str, any]) -> str:
    encoded = urlsafe_b64encode(dumps(claims).encode("utf-8")).decode("utf-8")
    return f"header.{encoded}.sign"


@mark.parametrize(
    "claims, is_expired",
    (
        (None, False),
        ({}, False),
        ({"exp": datetime.now().timestamp() + 10}, False),
        ({"exp": datetime.now().timestamp() - 10}, True),
    ),
)
def test_jwt_expired(claims: Dict[str, any], is_expired):
    token = _encode(claims)
    assert is_expired_token(token) == is_expired


@mocketize(strict_mode=True)
@mark.parametrize(
    "mocket_args, exception",
    (({"status": 403}, AuthError), ({"exception": error()}, URLError)),
)
def test_auth_token_failure(memory_cache, mocket_args: Dict, exception):
    auth = Auth(client_id="test", client_secret="test", cache=memory_cache)

    Entry.single_register("POST", urljoin(auth.auth_url, "oauth/token"), **mocket_args)

    with raises(exception):
        auth.token()


@mocketize(strict_mode=True)
def test_auth_token(memory_cache):
    auth = Auth(client_id="test", client_secret="test", cache=memory_cache)

    Entry.single_register(
        "POST",
        urljoin(auth.auth_url, "oauth/token"),
        body=dumps({"access_token": "test-token"}),
    )

    assert auth.token() == "test-token"
