import pathlib

HERE = pathlib.Path(__file__).parent
MONOREPO = HERE.parent.parent
VENV = MONOREPO / ".venv"
PYTHON_BIN = VENV / "bin" / "python"
THIRD_PARTY = MONOREPO / "third-party"

HOME = pathlib.Path.home()
LOGS = HOME / ".human-compatible" / "logs"
UNIX_SOCKETS = HOME / ".human-compatible" / "unix-sockets"

SHIMS = HOME / ".asdf" / "shims"
NODE = SHIMS / "node"
YARN = SHIMS / "yarn"
