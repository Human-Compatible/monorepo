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

import asyncio
import json
import logging
from typing import Literal, cast

import aiofiles
from fastapi import APIRouter, Request

from assistance import _ctx
from assistance._config import ROOT_DOMAIN
from assistance._email.formatter import handle_reply_formatter
from assistance._faq.response import write_and_send_email_response
from assistance._keys import get_mailgun_api_key
from assistance._logging import log_info
from assistance._mailgun import send_email
from assistance._paths import NEW_EMAILS, get_emails_path
from assistance._types import Email, RawEmail
from assistance._utilities import get_cleaned_email, get_hash_digest

MAILGUN_API_KEY = get_mailgun_api_key()

router = APIRouter(prefix="/email")


@router.post("")
async def receive_email(request: Request):
    raw_email: RawEmail = await request.json()

    email_without_attachments = raw_email.copy()
    email_without_attachments["attachments"] = []

    logging.info(_ctx.pp.pformat(email_without_attachments))

    hash_digest = await _store_email(raw_email)

    asyncio.create_task(_handle_new_email(hash_digest, raw_email))

    return {"message": "Queued. Thank you."}


# TODO: Handle attachments
async def _store_email(raw_email: RawEmail):
    try:
        email_to_store = json.dumps(raw_email, indent=2)
    except TypeError:
        json_encodable_items = {}
        for key, item in raw_email.items():
            try:
                json.dumps(item)
                json_encodable_items[key] = item
            except TypeError:
                json_encodable_items[key] = str(item)

        email_to_store = json.dumps(json_encodable_items, indent=2)

    hash_digest = get_hash_digest(email_to_store)
    emails_path = get_emails_path(hash_digest, create_parent=True)

    async with aiofiles.open(emails_path, mode="w") as f:
        await f.write(email_to_store)

    pipeline_path = _get_new_email_pipeline_path(hash_digest)
    async with aiofiles.open(pipeline_path, mode="w") as f:
        pass

    return hash_digest


def _get_new_email_pipeline_path(hash_digest: str):
    return NEW_EMAILS / hash_digest


async def _handle_new_email(hash_digest: str, raw_email: RawEmail):
    """React to the new email, and once it completes without error, delete the pipeline file."""

    email = await _initial_parsing(raw_email)

    if email["agent_domain"] != ROOT_DOMAIN:
        logging.info("Email is not from the root domain. Breaking loop. Doing nothing.")
        return

    email_without_attachments = email.copy()
    email_without_attachments["attachments"] = []

    log_info(email["user_email"], _ctx.pp.pformat(email_without_attachments))

    await _react_to_email(email)

    pipeline_path = _get_new_email_pipeline_path(hash_digest)
    pipeline_path.unlink()


async def _react_to_email(email: Email):
    if email["mail_from"] == "forwarding-noreply@google.com":
        await _respond_to_gmail_forward_request(email)

        return

    if ROOT_DOMAIN in email["from"]:
        logging.info(
            f"Email is from a {ROOT_DOMAIN} agent. Breaking loop. Doing nothing."
        )
        return

    if email["agent_name"] == "jims-ac-faq":
        await write_and_send_email_response("jims-ac", email)

        return

    if email["agent_name"].startswith("reply-formatter"):
        await handle_reply_formatter(email=email)

        return

    logging.info("No handler found. Doing nothing.")

    return


async def _initial_parsing(raw_email: RawEmail):
    intermediate_email_dict = dict(raw_email.copy())

    keys_to_replace_with_empty_string_for_none: list[
        Literal[
            "cc",
            "in_reply_to",
            "replies_from_plain_body",
        ]
    ] = [
        "cc",
        "in_reply_to",
        "replies_from_plain_body",
    ]

    for key in keys_to_replace_with_empty_string_for_none:
        if intermediate_email_dict[key] is None:
            intermediate_email_dict[key] = ""

    intermediate_email_dict["plain_no_replies"] = str(
        intermediate_email_dict["plain_body"]
    )
    intermediate_email_dict["plain_replies_only"] = str(
        intermediate_email_dict["replies_from_plain_body"]
    )

    del intermediate_email_dict["plain_body"]
    del intermediate_email_dict["replies_from_plain_body"]

    intermediate_email_dict["plain_all_content"] = (
        intermediate_email_dict["plain_no_replies"]
        + intermediate_email_dict["plain_replies_only"]
    )

    to = str(intermediate_email_dict["to"])
    rcpt_to = str(intermediate_email_dict["rcpt_to"])

    agent_name, agent_domain = rcpt_to.split("@")

    intermediate_email_dict["agent_name"] = agent_name.lower()
    intermediate_email_dict["agent_domain"] = agent_domain.lower()

    cleaned_to = get_cleaned_email(to.lower())
    cleaned_rcpt_to = get_cleaned_email(rcpt_to.lower())

    if cleaned_rcpt_to != cleaned_to:
        # This is a forwarded email
        intermediate_email_dict["user_email"] = cleaned_to
    else:
        intermediate_email_dict["user_email"] = get_cleaned_email(
            str(intermediate_email_dict["from"])
        )

    email = cast(Email, intermediate_email_dict)

    return email


VERIFICATION_TOKEN_BASE = "https://mail.google.com/mail/vf-"
VERIFICATION_TOKEN_BASE_ALTERNATIVE = "https://mail-settings.google.com/mail/vf-"


async def _respond_to_gmail_forward_request(email: Email):
    forwarding_email = email["to"]

    found_token = None

    for item in email["plain_no_replies"].splitlines():
        log_info(email["user_email"], item)

        for option in [VERIFICATION_TOKEN_BASE, VERIFICATION_TOKEN_BASE_ALTERNATIVE]:
            if item.startswith(option):
                found_token = item.removeprefix(option)
                break

    assert found_token is not None

    await _post_gmail_forwarding_verification(found_token)

    user_email = email["plain_no_replies"].split(" ")[0]
    log_info(email["user_email"], f"User email: {user_email}")

    mailgun_data = {
        "from": forwarding_email,
        "to": [user_email],
        "subject": "Email forwarding approved",
        "plain_body": (
            "Hi!\n",
            f"We've approved your ability to be able to forward emails through to {forwarding_email}.",
        ),
    }

    await send_email(email["user_email"], mailgun_data)


async def _post_gmail_forwarding_verification(verification_token):
    forwarding_verification_post_url = f"{VERIFICATION_TOKEN_BASE}{verification_token}"
    logging.info(forwarding_verification_post_url)

    post_response = await _ctx.session.post(url=forwarding_verification_post_url)

    logging.info(await post_response.read())
