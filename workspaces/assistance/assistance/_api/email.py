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
import logging

import aiofiles
from fastapi import APIRouter, Request

from assistance import _ctx
from assistance._email.handler import (
    get_json_representation_of_raw_email,
    get_new_email_pipeline_path,
    handle_new_email,
)
from assistance._paths import get_emails_path
from assistance._types import RawEmail
from assistance._utilities import get_hash_digest

router = APIRouter(prefix="/email")


@router.post("")
async def receive_email(request: Request):
    raw_email: RawEmail = await request.json()

    email_without_attachments = raw_email.copy()
    email_without_attachments["attachments"] = []

    logging.info(_ctx.pp.pformat(email_without_attachments))

    hash_digest = await _store_email(raw_email)

    asyncio.create_task(handle_new_email(hash_digest, raw_email))

    return {"message": "Queued. Thank you."}


# TODO: Handle attachments
async def _store_email(raw_email: RawEmail):
    email_to_store = get_json_representation_of_raw_email(raw_email)

    hash_digest = get_hash_digest(email_to_store)
    emails_path = get_emails_path(hash_digest, create_parent=True)

    async with aiofiles.open(emails_path, mode="w") as f:
        await f.write(email_to_store)

    pipeline_path = get_new_email_pipeline_path(hash_digest)
    async with aiofiles.open(pipeline_path, mode="w") as f:
        pass

    return hash_digest
