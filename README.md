# SatelliteVu Platform API Client SDK

Lightweight API Client SDK for SatelliteVu's Platform APIs, providing authorization
handling and convenience methods to interact wit the published APIs.

## Installation

TBD

For now, need to use the repo as an git based dependency. Can use the `requests` or
`httpx` optional dependency groups, as these http client implementations can be used
instead of the default urllib based client.

## Usage

A User API Client credential set consisting of an _client id_ and _client secret_ is
needed and should be set in your script's environment variables.

Check out the [examples](./examples/) provided. They can for example be run locally with

```
poetry run python ./examples/archive.py --example=recent
```

### Simple Client Usage

The easiest way to get started is to use the `satellitevu.Client` class, which needs
a client_id and client_secret only:

```
import os

from satellitevu import Client


client = Client(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
print(client.archive_v1.search().json())
```

`client.archive_v1.search` supports all supported request body parameters documented
in the [API docs](search-api-docs), with special handling for `datetime` which is
constructed from the optional `date_from` and `date_to` parameters and a default result
page size limit of 25.

### Authentication Handling

The `satellitevu.Auth` class provides the main interface to retrieve an
authorization token required to interact with the API endpoints.

```
import os

from satellitevu import Auth


auth = Auth(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
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

## Developer Setup

### Requirements

- Installations of Python 3.8 and 3.10 (for example using [Pyenv][pyenv])
- Global installations (for example managed with [pipx][pipx]) of
  - Python [Poetry](poetry)
  - Python [nox](nox) with [nox-poetry](nox-poetry) plugin
- Make (optional)

Example global setup (with `pyenv` and `pipx`):

```
pyenv install 3.8.13
pyenv install 3.10.4
pipx install poetry
pipx install nox
pipx inject nox nox-poetry
```

Please bootstrap your environment with `make bootstrap`.

#### Example test setup with `pyenv` and `pipx`

Run tests against Python version used by poetry:

```
make test
make PYTEST_ADDOPTS="-x -s" test
```

or

```
poetry run pytest
PYTEST_ADDOPTS="-x -s" poetry run pytest
```

Run tests against Python 3.8 and Python 3.10:

```
pyenv shell 3.8.13 3.10.4
nox
```

[pyenv]: https://github.com/pyenv/pyenv
[poetry]: https://python-poetry.org
[pipx]: https://pypa.github.io/pipx/
[nox]: https://nox.thea.codes/en/stable/
[nox-poetry]: https://nox-poetry.readthedocs.io/en/stable/
[search-api-docs]: https://api.satellitevu.com/archive/v1/docs#operation/Search_search_post
