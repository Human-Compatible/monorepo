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

import aiocron
import tomlkit

from assistance._email.formatter import _get_reply_template
from assistance._email.handler import initial_parsing
from assistance._git import pull, push
from assistance._paths import LOCAL_EMAIL_RECORD, SYNCED_JIMS_REPO, get_emails_path

IGNORE_EMAIL_STRINGS = ["Ready to Launch"]


@aiocron.crontab("0 15 * * *")
async def tasker_faq_update():
    await run_faq_update()


async def run_faq_update():
    logging.info("Running FAQ update")

    pull()
    await _update_faq()

    push("Push of data after FAQ update")


async def _update_faq():
    faq_path = SYNCED_JIMS_REPO / "faqs.toml"

    with open(faq_path) as f:
        faq_data = tomlkit.load(f)

    collected_questions = {
        item["question"].strip().replace("\n", " "): item["answer"]
        for item in faq_data["items"]  # type: ignore
    }

    receiver = {}

    for path in LOCAL_EMAIL_RECORD.glob("*/*/*.json"):
        with open(path) as f:
            try:
                receiver[path.stem] = json.load(f)["rcpt_to"]
            except:
                pass

    email_to_match = "reply-formatter"

    found_email_hashed = [
        key
        for key, item in receiver.items()
        if item is not None and email_to_match in item
    ]

    for email_hash in found_email_hashed:
        path = get_emails_path(email_hash)

        with open(path) as f:
            email = await initial_parsing(json.load(f))

        _subject, content = _get_reply_template(email)

        current_qna = [item for item in content.split("\n\n") if item.startswith("Q:")]

        _append_qna_to_collected_questions(collected_questions, current_qna)

    data_for_saving = {
        "items": [
            {
                "question": key,
                "answer": tomlkit.string(f"\n{item.strip()}\n", multiline=True),
            }
            for key, item in collected_questions.items()
        ]
    }

    with open(faq_path, "w") as f:
        tomlkit.dump(data_for_saving, f)


def _append_qna_to_collected_questions(collected_questions, current_qna):
    for item in current_qna:
        question, answer = item.split("\nA: ")
        question = question.strip().replace("\n", " ").removeprefix("Q: ")

        for ignore_string in IGNORE_EMAIL_STRINGS:
            if ignore_string in answer.replace("\n", " "):
                return

        if question in collected_questions:
            continue

        collected_questions[question] = answer
