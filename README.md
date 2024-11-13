# SatelliteVu SDK for Python

[![pypi](https://img.shields.io/pypi/v/satellitevu)](https://pypi.org/project/satellitevu/)
[![license](https://img.shields.io/github/license/SatelliteVu/satellitevu-client-python)](https://github.com/SatelliteVu/satellitevu-client-python/blob/main/LICENSE)
[![Twitter](https://img.shields.io/twitter/follow/satellitevu?style=social)](https://twitter.com/intent/follow?screen_name=satellitevu)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin)](https://uk.linkedin.com/company/satellitevu)

Lightweight API Client SDK for SatelliteVu's Platform APIs, providing authorization
handling and convenience methods to interact with the published APIs.

## Installation

The package is published to [PyPi][pypi] and can be installed with pip:

```
pip install satellitevu
```

Currently Python 3.8, 3.10 and 3.11 are supported.

## Usage

A User API Client credential set consisting of an _client id_ and _client secret_ is
needed and should be set in your script's environment variables.

Check out the [examples][examples] provided. They can for example be run locally with

```
poetry run python ./examples/catalog.py --example=recent
```

### Simple Client Usage

The easiest way to get started is to use the `satellitevu.Client` class, which needs
a client_id and client_secret only:

```
import os

from satellitevu import Client


client = Client(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
contract_id = os.getenv("CONTRACT_ID")
print(client.catalog_v1.search(contract_id=contract_id).json())
```

`client.catalog_v1.search` supports all request body parameters documented
in the [API docs][search-api-docs], with special handling for `datetime` which is
constructed from the optional `date_from` and `date_to` parameters and a default result
page size limit of 25.

### Authentication Handling

The `satellitevu.Auth` class provides the main interface to retrieve an
authorization token required to interact with the API endpoints.

```
import os

from satellitevu import Auth


auth = Auth(client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"))
print(auth.token())
```

Thus retrieved token can be used for bearer token authentication in HTTP request
Authorization headers.

The `Auth` class by default uses a file based cache which will store the token in

- `~/.cache/SatelliteVu` on Linux
- `~/Library/Caches/SatelliteVu` on MacOS
- `C:\Documents and Settings\<username>\Local Settings\Application Data\SatelliteVu\Cache`
  on Windows

Other cache implementations must implement the `satellitevu.auth.cache.AbstractCache`
class.

### HTTP Client Wrappers

Convenience wrapper classes for common HTTP client implementations are provided as
implementations of `satellitevu.http.AbstractClient`, which provides an `request` method
with an interface similar to `requests.request` and returning an
`satellitevu.http.ResponseWrapper` instance, where the response object of the underlying
implementation is available in the `raw` property.

Commonly used properties and methods are exposed on both `AbstractClient` and
`ResponseWrapper`.

- `satellitevu.http.UrllibClient` for Python standard lib's `urllib`
- `satellitevu.http.requests.RequestsSession` using `requests.Session` class
- `satellitevu.http.httpx.HttpxClient` using `httpx.Client` (Todo)

Implementations based on `requests` and `httpx` allow setting an instance of the
underlying implementation, but will provide a default instance if not.

[pyenv]: https://github.com/pyenv/pyenv
[poetry]: https://python-poetry.org
[pipx]: https://pypa.github.io/pipx/
[nox]: https://nox.thea.codes/en/stable/
[nox-poetry]: https://nox-poetry.readthedocs.io/en/stable/
[search-api-docs]: https://api.satellitevu.com/catalog/v2/docs#operation/Search_search_post
[pypi]: https://pypi.org/project/satellitevu/
[examples]: https://github.com/SatelliteVu/satellitevu-client-python/tree/main/examples
