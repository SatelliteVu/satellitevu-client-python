# SatelliteVu Platform API Client SDK

Lightweight API Client SDK for SatelliteVu's Platform APIs, providing authorization
handling and convenience methods to interact wit the published APIs.

## Installation

TBD

## Usage

A User API Client credential set consisting of an _client id_ and _client secret_ is
needed and should be set in your script's environment variables.

### Authentication Handling

The `satellitevu.auth.Auth` class provides the main interface to retrieve an
authorization token required to interact with the API endpoints.

```
from os import getenv

from satellitevu.auth import Auth


auth = Auth(getenv("CLIENT_ID"), getenv("CLIENT_SECRET"))
print(auth.token)
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
- `satellitevu.http.requests.` using `requests.Session` class
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
