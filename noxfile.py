from nox_poetry import session

PYTHON_VERSIONS = ("3.10", "3.8")


@session(python=PYTHON_VERSIONS)
def tests(session):
    session.install(
        "pytest",
        "pyfakefs",
        "mocket",
        "pytest-cov",
        "requests",
        "httpx",
        ".",
    )
    session.run("pytest", "--cov=satellitevu")
