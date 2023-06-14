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

from assistance._logging import log_info

from . import _ctx
from ._config import ROOT_DOMAIN
from ._keys import get_postal_api_key

EMAIL_SUBJECT = f"Your career.{ROOT_DOMAIN} access link"
EMAIL_TEMPLATE = (
    "Your personal access link, which is tied to your email is {access_link}"
)
LINK_TEMPLATE = "https://career.{domain}/?pwd={password}"

POSTAL_API_KEY = get_postal_api_key()


async def send_email(scope: str, postal_data):
    headers = {
        "Content-Type": "application/json",
        "X-Server-API-Key": POSTAL_API_KEY,
    }

    url = "https://postal.assistance.chat/api/v1/send/message"

    if "cc" in postal_data and postal_data["cc"] == "":
        del postal_data["cc"]

    log_info(scope, json.dumps(postal_data, indent=2))

    postal_response = await _ctx.session.post(
        url=url,
        headers=headers,
        data=json.dumps(postal_data),
    )

    log_info(scope, json.dumps(await postal_response.json(), indent=2))
