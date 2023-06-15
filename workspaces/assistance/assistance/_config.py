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

import json
import pathlib
import tomllib
from typing import TypedDict, cast

import aiofiles

from assistance._paths import SYNCED_FAQS_STORE

GPT_TURBO_SMALL_CONTEXT = "gpt-3.5-turbo-0613"
GPT_TURBO_LARGE_CONTEXT = "gpt-3.5-turbo-16k"
GPT_SOTA = "gpt-4-0314"

SUPERVISION_SUBJECT_FLAG = "[SUPERVISION TASK]"

ROOT_DOMAIN = "assistance.chat"
PAYMENT_LINK = "https://buy.stripe.com/bIYeXF2s1d0E4wg9AB"
EMAIL_PRODUCT_ID = "prod_NLuYISl8KZ6fUX"

POSTAL_DOMAIN = f"postal.{ROOT_DOMAIN}"
POSTAL_API_URL = f"https://{POSTAL_DOMAIN}/api/v1/send"

POSTAL_MESSAGE_API_URL = f"{POSTAL_API_URL}/message"
POSTAL_RAW_API_URL = f"{POSTAL_API_URL}/raw"


class QAndAItem(TypedDict):
    question: str
    answer: str


class FaqData(TypedDict):
    items: list[QAndAItem]


async def load_faq_data():
    async with aiofiles.open(SYNCED_FAQS_STORE, encoding="utf8") as f:
        data = cast(FaqData, tomllib.loads(await f.read()))

    return data


async def get_file_based_mapping(root: pathlib.Path, user: str, include_user=True):
    user_details_files = (root / user).glob("*")
    details = {}

    if include_user:
        details["user"] = user

    for file in user_details_files:
        assert file.name != "user"

        async with aiofiles.open(file) as f:
            file_contents = (await f.read()).strip()

        if file.name.endswith(".json"):
            details[file.name[:-5]] = json.loads(file_contents)
            continue

        details[file.name] = file_contents

    return details
