from nox_poetry import session

PYTHON_VERSIONS = ("3.10", "3.8")


@session()
def lint(session):
    session.install("flake8", "black", "isort")
    session.run("black", ".")
    session.run("flake8", ".")
    session.run("isort", ".")


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
    session.run("pytest")
