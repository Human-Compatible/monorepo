# Copyright (C) 2022 Assistance.Chat contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from ._logging import log_info

from . import _ctx
from ._keys import get_postal_api_key
from ._config import POSTAL_MESSAGE_API_URL


POSTAL_API_KEY = get_postal_api_key()


async def send_email(scope: str, postal_data):
    headers = {
        "Content-Type": "application/json",
        "X-Server-API-Key": POSTAL_API_KEY,
    }

    if "cc" in postal_data and postal_data["cc"] == "":
        del postal_data["cc"]

    log_info(scope, json.dumps(postal_data, indent=2))

    postal_response = await _ctx.session.post(
        url=POSTAL_MESSAGE_API_URL,
        headers=headers,
        data=json.dumps(postal_data),
    )

    log_info(scope, json.dumps(await postal_response.json(), indent=2))
