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
import logging
import random
from typing import Literal, cast

from assistance import _ctx
from assistance._config import ROOT_DOMAIN
from assistance._email.formatter import handle_reply_formatter
from assistance._faq.response import write_and_send_email_response
from assistance._logging import log_info
from assistance._paths import NEW_EMAILS
from assistance._postal import send_email
from assistance._types import Email, RawEmail
from assistance._utilities import get_cleaned_email


async def handle_new_email(hash_digest: str, raw_email: RawEmail):
    """React to the new email, and once it completes without error, delete the pipeline file."""

    try:
        email = await _initial_parsing(raw_email)

        if email["agent_domain"] != ROOT_DOMAIN:
            logging.info(
                "Email is not from the root domain. Breaking loop. Doing nothing."
            )

        else:
            email_without_attachments = email.copy()
            email_without_attachments["attachments"] = []

            log_info(email["user_email"], _ctx.pp.pformat(email_without_attachments))

            await _react_to_email(email)

        pipeline_path = get_new_email_pipeline_path(hash_digest)
        pipeline_path.unlink()

    except Exception as e:  # pylint: disable=broad-except
        await _send_error_email(e, raw_email)
        raise


async def rerun():
    """Select a random hash from the new email pipeline, and then rerun the handler."""

    pipeline_paths = list(NEW_EMAILS.glob("*"))
    if not pipeline_paths:
        logging.info("No new emails to rerun.")
        return

    pipeline_path = random.choice(pipeline_paths)
    hash_digest = pipeline_path.name

    with pipeline_path.open() as f:
        raw_email = json.load(f)

    await handle_new_email(hash_digest, raw_email)


def get_json_representation_of_raw_email(raw_email: RawEmail):
    try:
        return json.dumps(raw_email, indent=2)
    except TypeError:
        pass

    json_encodable_items = {}
    for key, item in raw_email.items():
        try:
            json.dumps(item)
            json_encodable_items[key] = item
        except TypeError:
            json_encodable_items[key] = str(item)

    return json.dumps(json_encodable_items, indent=2)


def get_new_email_pipeline_path(hash_digest: str):
    return NEW_EMAILS / hash_digest


async def _send_error_email(exception: Exception, raw_email: RawEmail):
    json_rep_of_email = get_json_representation_of_raw_email(raw_email)

    postal_data = {
        "from": "error-notification@assistance.chat",
        "to": ["me@simonbiggs.net", "cameron.richardson@ac.edu.au"],
        "subject": "[ERROR NOTIFICATION]",
        "plain_body": (
            f"When handling an email the following error occurred\n\n{exception}\n\nThe details of the email received were:\n\n{json_rep_of_email}"
        ),
    }

    await send_email("handling error", postal_data)


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
        await write_and_send_email_response(email)

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
