# Design

Architectural overview of the SatelliteVu SDK for Python.

## Introduction

The SatelliteVu SDK for Python is composed of lightweight modules providing configurable
classes. Each class provides sensible defaults to get easily started while allowing
custom configurations and implementations to build specific environments.

## HTTP Client

As an SDK for REST APIs, providing an HTTP client is essential. A client class requiring
only the `urllib` package in the Python Standard Library is provided in
[satellitevu.http.urllib.UrllibClient](./satellitevu/http/urllib.py). This is the
default client class used when no other is specified.

All clients wrap their responses in an instance of
[satellitevu.http.base.ResponseWrapper](./satellitevu/http/base.py) with the original
response available in the `raw` property.

### `requests` and `httpx` support

When `httpx` or `requests` is installed, alternative HTTP client classes from
[satellitevu.http.httpx.HttpxClient](./satellitevu/http/httpx.py) or
[satellitevu.http.requests.RequestsSession](./satellitevu/http/requests.py) can be used.

## Auth Helper

The workflow of getting an access token from the OIDC API is managed in the
[satellitevu.Auth](./satellitevu/auth/auth.py) class, which offers a `token()` method to
allow the the requested scopes to be represented within the returned access token.

See [examples/auth.py](./examples/auth.py) for an example of how to use it.

### Auth Cache

To avoid hitting token request rate limits, the Auth class utilizes a cache - by default
an instance of [satellitevu.auth.AppDirCache](./satellitevu/auth/cache.py) is used. Any
class implementing the
[satellitevu.auth.cache.AbstractCache](./satellitevu/auth/cache.py) can be passed to the
Auth class constructor instead, if you wish so.

The AppDirCache cache uses a simple file based cache in the cache dir of the current
user. This is the reason for our only required dependency,
[appdirs](https://pypi.org/project/appdirs/).

## Platform Client

### Platform API classes

Classes for each available API are maintained in
[satellitevu.apis](./satellitevu/apis/), i.e. for the Archive API and Orders API. They
use the [satellitevu.apis.base.AbstractApi](./satellitevu/apis/base.py) base class for
building URLs, sending requests and raising exceptions.

### Main client class

Using all of the above, the main client [satellitevu.Client](./satellitevu/client.py),
provides the central entry point to interacting with our platform APIs.

See [examples/archive.py](./examples/archive.py) for an example of how to use it.
