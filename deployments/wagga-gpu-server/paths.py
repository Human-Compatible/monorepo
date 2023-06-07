import pathlib

HERE = pathlib.Path(__file__).parent
MONOREPO = HERE.parent.parent
THIRD_PARTY = MONOREPO / "third-party"

HOME = pathlib.Path.home()
SHIMS = HOME / ".asdf" / "shims"
NODE = SHIMS / "node"
YARN = SHIMS / "yarn"
