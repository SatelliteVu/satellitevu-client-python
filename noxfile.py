from nox_poetry import session

PYTHON_VERSIONS = ("3.9", "3.10", "3.11")


@session()
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "--fix")
    session.run("ruff", "format")


@session(python=PYTHON_VERSIONS)
def tests(session):
    session.install(
        "pytest",
        "pyfakefs",
        "mocket",
        "pytest-cov",
        "requests",
        "httpx",
        "cryptography",
        "josepy",
        "pyjwt",
        "pact-python",
        ".",
    )
    session.run("pytest")
