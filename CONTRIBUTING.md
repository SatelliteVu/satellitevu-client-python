# Contributing

We encourage contributions of code and documentation. Please read this document to learn
how to make the contribution process smooth.

# Development Setup

## Requirements

- Installations of Python 3.8 and 3.10 (for example using [Pyenv][pyenv])
- Global installations (for example managed with [pipx][pipx]) of
  - Python [Poetry][poetry]
  - Python [nox][nox] with [nox-poetry][nox-poetry] plugin
- Make (optional)

Example global setup (with `pyenv` and `pipx`):

```
pyenv install 3.8.13
pyenv install 3.10.4
pipx install poetry
pipx install nox
pipx inject nox nox-poetry
```

Please bootstrap then your environment with `make bootstrap`.

## Linting and Testing

Using pyenv, activate the Python version to be tested against, then run linting and test
suites with nox:

```
pyenv shell 3.8.13 3.10.4
nox --session=linting
nox --session=tests
```

An example of running only against one Python version with additional options for
pytest:

```
PYTEST_ADDOPTS="--cov=satellitevu" nox --session=tests --python=3.10
```

## Documentation

# Pull Requests

## Required branch names

We use branch names to identify how the version will need to be updated once merged. In
a nutshell, every branch name must start with either `patch/`, `minor/` or `major/` to
trigger the semantic versioning bump rule. PRs with branch names not following this
pattern will fail.
