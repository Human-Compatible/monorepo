# Copyright (C) 2023 Assistance.Chat contributors

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
from typing import Any, Literal, TypedDict, cast

import aiofiles

from assistance._paths import (
    AGENT_MAPPING,
    CONFIG,
    EMAIL_MAPPING,
    FAQ_DATA,
    USER_DETAILS,
)

SIMPLER_OPENAI_MODEL = "gpt-3.5-turbo"
SOTA_OPENAI_MODEL = "gpt-4"

SUPERVISION_SUBJECT_FLAG = "[SUPERVISION TASK]"

ROOT_DOMAIN = "assistance.chat"
PAYMENT_LINK = "https://buy.stripe.com/bIYeXF2s1d0E4wg9AB"
EMAIL_PRODUCT_ID = "prod_NLuYISl8KZ6fUX"

TargetedNewsFormats = Literal["digest", "discourse"]


class TargetedNewsUserOverrides(TypedDict, total=False):
    delivery_time: str
    delivery_timezone: str
    delivery_frequency: str
    goals: list[str]
    tasks: list[str]


class TargetedNewsSubscriptionDataItem(TypedDict):
    target_audience: str
    sentence_blacklist: list[str]
    keywords: list[str]
    agent_user: str
    format: TargetedNewsFormats
    subscribers: list[str]
    user_overrides: dict[str, TargetedNewsUserOverrides]


class TargetedNewsConfig(TypedDict):
    delivery_time: str
    delivery_timezone: str
    delivery_frequency: str
    goals: list[str]
    goal_weights: list[float]
    tasks: list[str]
    task_weights: list[float]
    subscription_data: list[TargetedNewsSubscriptionDataItem]


def get_google_oauth_client_id():
    return _load_config_item("google-oauth-client-id")


def _load_config_item(name: str):
    path = CONFIG / name

    with open(path, encoding="utf8") as f:
        item = f.read().strip()

    return item


async def load_targeted_news_config() -> TargetedNewsConfig:
    async with aiofiles.open(CONFIG / "targeted-news.toml", "r") as f:
        news_config = cast(TargetedNewsConfig, tomllib.loads(await f.read()))

    return news_config


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
