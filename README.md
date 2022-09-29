# SatelliteVu Platform API Client SDK

## Installation

TBD

## Usage

TBD

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
```

or

```
poetry run pytest
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
