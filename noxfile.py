import nox

nox.options.sessions = ["test", "quality"]
nox.options.pythons = ["3.8"]


DEP_PYTEST = ["pytest~=7.4"]
DEP_TEST = ["pytest-asyncio", *DEP_PYTEST]
DEP_PYLINT = ["pylint~=3.0"]
DEP_BLACK = ["black~=23.11"]
DEP_LINT = [*DEP_PYLINT, *DEP_PYTEST]


@nox.session(python=["3.8", "3.9", "3.10"])
def test(session: nox.Session) -> None:
    """
    Run unit tests for change-ls
    """
    build_mock_server(session)
    build_token_server(session)
    session.install("-e", ".")
    session.install(*DEP_TEST)
    session.run("pytest", "-m", "not uses_external_resources", "test")


@nox.session(python=["3.8"])
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
    res = bool(
        session.run(
            "python",
            "-c",
            "from change_ls.tokens import check_node_version; print(check_node_version())",
            silent=True,
        )
    )
    if not res:
        session.skip("The installed node version is not compatible with change-ls.")


@nox.session(python=["3.8"])
def build_mock_server(session: nox.Session) -> None:
    """
    Builds the mock language server used for testing.
    """
    check_node_version(session)
    with session.chdir("mock-server"):
        session.run("npm", "ci", external=True)
        session.run("npm", "run", "build", external=True)


@nox.session(python=["3.8"])
def build_token_server(session: nox.Session) -> None:
    """
    Builds the token server used for syntactic tokenization.
    """
    check_node_version(session)
    with session.chdir("token-server"):
        session.run("npm", "ci", external=True)
        session.run("npm", "run", "build", external=True)


@nox.session(python=["3.8"])
def test_generator(session: nox.Session) -> None:
    """
    Runs the tests for the change-ls code generator.
    """
    session.install(*DEP_TEST)
    session.run("pytest", "gen/test")


@nox.session(python=["3.8"])
def generate_lsp_types(session: nox.Session) -> None:
    """
    Generates the code for the LSP types at ``change_ls/types``.
    """
    test_generator(session)
    session.run("python", "-m", "gen.main", "./res", "./change_ls/types")


@nox.session(python=["3.8"])
def reformat(session: nox.Session) -> None:
    """
    Reformat the code using Black.
    """
    session.install(*DEP_BLACK)
    session.run("black", "change_ls", "gen", "test")


@nox.session(python=["3.8"])
def check_formatting(session: nox.Session) -> None:
    """
    Check whether the code adheres to the configured style using Black.
    """
    session.install(*DEP_BLACK)
    session.run("black", "--check", "change_ls", "gen", "test")


@nox.session(python=["3.8"])
def lint(session: nox.Session) -> None:
    """
    Perform linting using pylint.
    """
    session.install(*DEP_LINT)
    session.run("pylint", "--disable=R,C", "change_ls", "gen")


@nox.session(python=["3.8"])
def typecheck(session: nox.Session) -> None:
    """
    Perform type checking using pyright.
    """
    check_node_version(session)
    session.install(*DEP_PYTEST)
    session.run(
        "npm", "exec", "--package", "pyright@1.1.335", "--yes", "--", "pyright", external=True
    )
