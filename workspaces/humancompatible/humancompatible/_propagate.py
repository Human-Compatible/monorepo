# Copyright (C) 2020-2023 Simon Biggs

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pathlib
import json
import re
import subprocess
import textwrap

import black
import tomlkit
from tomlkit.items import Table, Item

from ._paths import MONOREPO

POETRY_LOCK_PATH = MONOREPO / "poetry.lock"

AUTOGEN_MESSAGE = [
    "DO NOT EDIT THIS FILE!",
    "This file has been autogenerated by `make propagate`",
]


def main():
    for workspace in (MONOREPO / "workspaces").iterdir():
        pyproject_path = workspace / "pyproject.toml"

        if pyproject_path.exists():
            version_path = workspace / workspace.name / "_version.py"

            _propagate_version(pyproject_path, version_path)
            _propagate_extras(pyproject_path)

    _update_poetry_lock()


def _propagate_version(pyproject_path: pathlib.Path, version_path: pathlib.Path):
    version_string = get_version_string(pyproject_path)
    version_list = re.split(r"[-\.]", version_string)

    for i, item in enumerate(version_list):
        try:
            version_list[i] = int(item)
        except ValueError:
            pass

    version_contents = textwrap.dedent(
        f"""\
        # {AUTOGEN_MESSAGE[0]}
        # {AUTOGEN_MESSAGE[1]}

        version_info = {version_list}
        __version__ = "{version_string}"
        """
    )

    version_contents = black.format_str(version_contents, mode=black.FileMode())

    with open(version_path, "w") as f:
        f.write(version_contents)


def _propagate_extras(pyproject_path: pathlib.Path):
    pyproject_contents = _read_pyproject(pyproject_path)

    poetry = _get_poetry_from_pyproject_contents(pyproject_contents)

    deps = poetry["dependencies"]
    assert isinstance(deps, Table)

    raw_new_extras = {}

    for key in deps:
        value = deps[key]
        assert isinstance(value, Item)

        comment = value.trivia.comment

        if comment.startswith("# extras"):
            split = comment.split("=")
            assert len(split) == 2
            groups = json.loads(split[-1])

            for group in groups:
                try:
                    raw_new_extras[group].append(key)
                except KeyError:
                    raw_new_extras[group] = [key]

    for group, deps in raw_new_extras.items():
        raw_new_extras[group] = sorted(deps)

    new_extras = tomlkit.item(raw_new_extras, _parent=poetry, _sort_keys=True)
    new_extras.trivia.comment = "\n# Autogenerated by `make propagate`"

    for _, deps in new_extras.items():
        if len(deps.as_string()) > 88:
            deps.multiline(True)

    try:
        old_extras = poetry["extras"]
    except KeyError:
        pass
    else:
        assert isinstance(old_extras, Table)
        if old_extras == new_extras:
            return

    if len(new_extras) == 0:
        return

    poetry["extras"] = new_extras

    with open(pyproject_path, "w") as f:
        f.write(tomlkit.dumps(pyproject_contents))


def _update_poetry_lock():
    subprocess.check_call(["poetry", "lock", "--no-update"], cwd=MONOREPO)


def get_version_string(pyproject_path):
    pyproject_contents = _read_pyproject(pyproject_path)
    poetry = _get_poetry_from_pyproject_contents(pyproject_contents)
    version_string = poetry["version"]

    return str(version_string)


def _read_pyproject(pyproject_path: pathlib.Path):
    with open(pyproject_path) as f:
        pyproject_contents = tomlkit.loads(f.read())

    return pyproject_contents


def _get_poetry_from_pyproject_contents(
    pyproject_contents: tomlkit.TOMLDocument,
) -> Table:
    tool = pyproject_contents["tool"]
    assert isinstance(tool, Table)

    poetry = tool["poetry"]
    assert isinstance(poetry, Table)

    return poetry
