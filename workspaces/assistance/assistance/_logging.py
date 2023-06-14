# Copyright (C) 2023 Simon Biggs

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import Any

from assistance import _ctx


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)d %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_info(scope: None | str, message: Any):
    if not isinstance(message, str):
        message = _ctx.pp.pformat(message)

    assert isinstance(message, str)

    if scope is None:
        logging.info(message)
        return

    logging.info(f"[{scope}] {message}")
