#!/usr/bin/python3

import subprocess

import paths


CAL_DIR = paths.THIRD_PARTY / "cal.com"


def main():
    env = {"PORT": "3431"}

    subprocess.check_call([paths.YARN, "start"], cwd=CAL_DIR, env=env)


if __name__ == "__main__":
    main()
