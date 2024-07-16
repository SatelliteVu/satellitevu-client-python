from nox_poetry import session

PYTHON_VERSIONS = ("3.10", "3.8", "3.11.0")


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
        "python-jose",
        ".",
    )
    session.run("pytest")
