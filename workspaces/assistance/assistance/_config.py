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
from typing import Any, TypedDict, cast

import aiofiles

from assistance._paths import (
    AGENT_MAPPING,
    EMAIL_MAPPING,
    FAQ_DATA,
    USER_DETAILS,
)

GPT_TURBO_SMALL_CONTEXT = "gpt-3.5-turbo-0613"
GPT_TURBO_LARGE_CONTEXT = "gpt-3.5-turbo-16k"
GPT_SOTA = "gpt-4-0613"

SUPERVISION_SUBJECT_FLAG = "[SUPERVISION TASK]"

ROOT_DOMAIN = "assistance.chat"
PAYMENT_LINK = "https://buy.stripe.com/bIYeXF2s1d0E4wg9AB"
EMAIL_PRODUCT_ID = "prod_NLuYISl8KZ6fUX"

POSTAL_DOMAIN = f"postal.{ROOT_DOMAIN}"
POSTAL_API_URL = f"https://{POSTAL_DOMAIN}/api/v1/send"

POSTAL_MESSAGE_API_URL = f"{POSTAL_API_URL}/message"
POSTAL_RAW_API_URL = f"{POSTAL_API_URL}/raw"


async def get_user_from_email(email_address: str):
    try:
        async with aiofiles.open(EMAIL_MAPPING / email_address) as f:
            user = await f.read()
    except FileNotFoundError as e:
        raise ValueError("User not found") from e

    return user


async def get_user_details(user: str):
    details = await get_file_based_mapping(USER_DETAILS, user)

    return details


async def get_agent_mappings(user: str):
    details = await get_file_based_mapping(AGENT_MAPPING, user)

    return details


class ProgressionItem(TypedDict):
    key: str
    task: str
    fields_for_completion: list[str]
    attachment_handler: str | None
    always_run_at_least_once: bool
    # TODO: Better handling of these fields
    subject: str
    body: str


class FormConfig(TypedDict):
    defaults: dict[str, Any]
    options: dict[str, list[str]]
    progression: list[ProgressionItem]
    field: dict[str, Any]


async def load_faq_data(name: str):
    async with aiofiles.open(FAQ_DATA / f"{name}.toml", encoding="utf8") as f:
        data = cast(FormConfig, tomllib.loads(await f.read()))

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
