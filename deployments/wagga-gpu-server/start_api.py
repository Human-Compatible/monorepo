#!/usr/bin/python3

import subprocess

import paths


GUNICORN_API_SOCKET = paths.UNIX_SOCKETS / "gunicorn-api.sock"


def main():
    subprocess.check_call(
        [
            paths.PYTHON_BIN,
            "-m",
            "gunicorn",
            "assistance._api.main:app",
            "--name",
            "assistance",
            "--workers",
            "25",
            "--worker-class",
            "uvicorn.workers.UvicornWorker",
            "--user=simon",
            "--group=simon",
            f"--bind=unix:{GUNICORN_API_SOCKET}",
            "--log-level=info",
            "--log-file=-",
        ]
    )


if __name__ == "__main__":
    main()
