from pathlib import Path

import nox

MIN_PYTHON = "3.8"
SUPPORTED_PYTHONS = ["3.8", "3.9", "3.10"]


nox.options.sessions = ["init", "test", "quality"]
nox.options.pythons = ["3.8"]


DEP_PYTEST = ["pytest~=7.4"]
DEP_TEST = ["pytest-asyncio", *DEP_PYTEST]
DEP_PYLINT = ["pylint~=3.0"]
DEP_BLACK = ["black~=23.11"]
DEP_LINT = [*DEP_PYLINT, *DEP_PYTEST]
DEP_ALL = [*DEP_TEST, *DEP_PYLINT, *DEP_BLACK]

DEP_PYRIGHT = ["pyright@1.1.335"]


_initialized = False


@nox.session(python=MIN_PYTHON)
def init(session: nox.Session) -> None:
    """
    Initialize the repository for development and testing.

    Some sessions that require the repository to be initialized will call this
    session. Even if multiple sessions call ``init``, it will run at most once
    per nox invokation.

    When the command-line argument ``--initialized`` is passed to nox, ``init``
    assumes that the repository is already in an initialized state and does nothing.
    """
    global _initialized
    if _initialized or "--initialized" in session.posargs:
        return
    generate_lsp_types(session)
    build_token_server(session)
    build_mock_server(session)
    _initialized = True


@nox.session(python=SUPPORTED_PYTHONS)
def test(session: nox.Session) -> None:
    """
    Run unit tests for change-ls
    """
    init(session)
    session.install("-e", ".")
    session.install(*DEP_TEST)
    session.run("pytest", "-m", "not uses_external_resources", "test")


@nox.session(python=MIN_PYTHON)
def quality(session: nox.Session) -> None:
    """
    Run various code quality checks (type checking, linting).
    """
    init(session)
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


def build_mock_server(session: nox.Session) -> None:
    """
    Builds the mock language server used for testing.
    """
    check_node_version(session)
    with session.chdir("mock-server"):
        session.run("npm", "ci", external=True)
        session.run("npm", "run", "build", external=True)


def build_token_server(session: nox.Session) -> None:
    """
    Builds the token server used for syntactic tokenization.
    """
    check_node_version(session)
    with session.chdir("token-server"):
        session.run("npm", "ci", external=True)
        session.run("npm", "run", "build", external=True)


@nox.session(python=MIN_PYTHON)
def test_generator(session: nox.Session) -> None:
    """
    Runs the tests for the change-ls code generator.
    """
    session.install(*DEP_TEST)
    session.run("pytest", "gen/test")


@nox.session(python=MIN_PYTHON)
def generate_lsp_types(session: nox.Session) -> None:
    """
    Generates the code for the LSP types at ``change_ls/types``.
    """
    test_generator(session)
    session.run("python", "-m", "gen.main", "./res", "./change_ls/types")


@nox.session(python=MIN_PYTHON)
def reformat(session: nox.Session) -> None:
    """
    Reformat the code using Black.
    """
    init(session)
    session.install(*DEP_BLACK)
    session.run("black", "change_ls", "gen", "test")


@nox.session(python=MIN_PYTHON)
def check_formatting(session: nox.Session) -> None:
    """
    Check whether the code adheres to the configured style using Black.
    """
    init(session)
    session.install(*DEP_BLACK)
    session.run("black", "--check", "change_ls", "gen", "test")


@nox.session(python=MIN_PYTHON)
def lint(session: nox.Session) -> None:
    """
    Perform linting using pylint.
    """
    init(session)
    session.install(*DEP_LINT)
    session.run("pylint", "--disable=R,C", "change_ls", "gen")


@nox.session(python=MIN_PYTHON)
def typecheck(session: nox.Session) -> None:
    """
    Perform type checking using pyright.
    """
    init(session)
    session.install(*DEP_PYTEST)
    session.run(
        "npm", "exec", "--package", *DEP_PYRIGHT, "--yes", "--", "pyright", external=True
    )


def _get_python_in_virtualenv(session: nox.Session) -> str:
    devenv_name = ".venv"
    if "--name" in session.posargs:
        name_index = session.posargs.index("--name")
        if name_index + 1 < len(session.posargs):
            devenv_name = session.posargs[name_index + 1]

    devenv_location = Path("./" + devenv_name)
    session.install("virtualenv")
    session.run("virtualenv", str(devenv_location), "--python", "cpython" + MIN_PYTHON)

    devenv_python = devenv_location / Path("bin/python")
    if not devenv_python.exists():
        devenv_python = devenv_location / Path("Scripts/python.exe")

    return str(devenv_python)


@nox.session(python=MIN_PYTHON)
def install_dev_dependencies(session: nox.Session) -> None:
    """
    Installs development dependencies.
    """
    # This is called from the Dockerfile, so it needs to be able to
    # install packages globally.
    session.run("pip", "install", *DEP_ALL)


@nox.session(python=MIN_PYTHON)
def devenv(session: nox.Session) -> None:
    """
    Sets up a virtual development environemnt.

    Use ``--global`` to install into the global environment.

    Use ``--name <name>`` to set the name for the development environment.
    The default name is ``.venv``.
    """
    init(session)

    if "--global" in session.posargs:
        python = "python3"
    else:
        python = _get_python_in_virtualenv(session)

    session.run(python, "-m", "pip", "install", "-e", ".", external=True)
    session.run(python, "-m", "pip", "install", *DEP_ALL, external=True)
