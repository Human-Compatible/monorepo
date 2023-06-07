#!/usr/bin/python3

import subprocess
import os

import paths


COMMON_ENVIRONMENT_VARIABLES = {"PROSE_APP_HOSTNAME": "127.0.0.1"}


CUSTOM_ENVIRONMENT_VARIABLES = {
    "GREENHOUSE": {
        "PROSE_DISCOURSE_HOST": "https://community.thegreenhouse.digital",
        "PROSE_APP_PORT": "8928",
    },
    "GUILD_OF_ENTREPRENEURS": {
        "PROSE_DISCOURSE_HOST": "https://discourse.guildofentrepreneurs.com",
        "PROSE_APP_PORT": "8929",
    },
    "ISA": {
        "PROSE_DISCOURSE_HOST": "https://c.internationalstudentassistance.com",
        "PROSE_APP_PORT": "8930",
    },
}


def main():
    env = {}
    env.update(COMMON_ENVIRONMENT_VARIABLES)
    try:
        prose_config = os.environ["PROSE_CONFIG"]
    except KeyError as e:
        raise RuntimeError("PROSE_CONFIG environment variable not set") from e

    if prose_config not in CUSTOM_ENVIRONMENT_VARIABLES:
        raise RuntimeError(f"Unknown PROSE_CONFIG: {prose_config}")

    env.update(CUSTOM_ENVIRONMENT_VARIABLES[prose_config])

    subprocess.check_call([paths.NODE, "lib/index.js"], cwd=paths.PROSE, env=env)


if __name__ == "__main__":
    main()
