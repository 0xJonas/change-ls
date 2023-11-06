import nox

nox.options.sessions = ["test", "quality"]


DEP_PYTEST = ["pytest"]
DEP_TEST = ["pytest-asyncio", *DEP_PYTEST]
DEP_PYLINT = ["pylint"]
DEP_BLACK = ["black"]


@nox.session
def test(session: nox.Session) -> None:
    """
    Run unit tests for change-ls
    """
    build_mock_server(session)
    build_token_server(session)
    session.install("-e", ".")
    session.install(*DEP_TEST)
    session.run("pytest", "-m", "not uses_external_resources", "test")


@nox.session
def quality(session: nox.Session) -> None:
    """
    Run various code quality checks (type checking, linting).
    """
    typecheck(session)
    check_formatting(session)
    lint(session)


def check_node_version(session: nox.Session) -> None:
    """
    Checks if the currently installed node version is sufficient for change-ls.
    """
    session.install("-e", ".")
    res = bool(session.run(
        "python",
        "-c",
        "from change_ls.tokens import check_node_version; print(check_node_version())",
        silent=True
    ))
    if not res:
        session.skip("The installed node version is not compatible with change-ls.")


@nox.session
def build_mock_server(session: nox.Session) -> None:
    """
    Builds the mock language server used for testing.
    """
    check_node_version(session)
    with session.chdir("mock-server"):
        session.run("npm", "run", "build", external=True)


@nox.session
def build_token_server(session: nox.Session) -> None:
    """
    Builds the token server used for syntactic tokenization.
    """
    check_node_version(session)
    with session.chdir("token-server"):
        session.run("npm", "run", "build", external=True)


@nox.session
def test_generator(session: nox.Session) -> None:
    """
    Runs the tests for the change-ls code generator.
    """
    session.install(*DEP_PYTEST)
    session.run("pytest", "-m", "gen/test")


@nox.session
def reformat(session: nox.Session) -> None:
    """
    Reformat the code using Black.
    """
    session.install(*DEP_BLACK)
    session.run("black", "change_ls", "gen", "test")


@nox.session
def check_formatting(session: nox.Session) -> None:
    """
    Check whether the code adheres to the configured style using Black.
    """
    session.install(*DEP_BLACK)
    session.run("black", "--check", "change_ls", "gen", "test")


@nox.session
def lint(session: nox.Session) -> None:
    """
    Perform linting using pylint.
    """
    session.install(*DEP_PYLINT)
    session.run("pylint", "--disable=R,C", "change_ls", "gen")


@nox.session
def typecheck(session: nox.Session) -> None:
    """
    Perform type checking using pyright.
    """
    check_node_version(session)
    session.install(*DEP_PYTEST)
    session.run(
        "npm", "exec", "--package", "pyright", "--yes", "--", "pyright", external=True
    )
