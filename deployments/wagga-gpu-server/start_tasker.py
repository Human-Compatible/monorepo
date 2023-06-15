#!/usr/bin/python3

import subprocess

import paths


def main():
    subprocess.check_call([paths.PYTHON_BIN, "-m", "assistance", "tasker"])


if __name__ == "__main__":
    main()
