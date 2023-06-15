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
import textwrap

from assistance._completion.summary import completion_on_thread_with_summary_fallback
from assistance._config import (
    GPT_SOTA,
    ROOT_DOMAIN,
    SUPERVISION_SUBJECT_FLAG,
    load_faq_data,
)
from assistance._email.reply import create_reply
from assistance._email.thread import get_email_thread
from assistance._keys import get_openai_api_key
from assistance._logging import log_info
from assistance._postal import send_email
from assistance._types import Email
from assistance._utilities import get_cleaned_email

from .answer import write_answer
from .correspondent import get_first_name
from .extract_questions import extract_questions

OPEN_AI_API_KEY = get_openai_api_key()

MODEL_KWARGS = {
    "engine": GPT_SOTA,
    "max_tokens": 1500,
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


PROMPT = textwrap.dedent(
    """
        # Write an email introduction and conclusion

        You are writing an email on behalf of Alex Carpenter.
        {first_name} is asking Alex questions about Jim's International
        Pathway Program. You are happy to help answer any questions that
        {first_name} may have about the Jim's International
        Pathway Program.

        You have been provided with a list of the answers to a range of
        questions that {first_name}. You are to write an introduction
        and conclusion to the email response to include around these
        questions and answers. Make sure to include the questions and
        answers in the same format you have been provided.

        You may remove components of answers if they are not appropriate
        within the context of the email. Do no add any extra information
        into any of the answers. If in your opinion the answer is not
        helpful please write "A:" without anything after it.

        Address {first_name} by their first name, unless it is not
        known. If it is not known simply start the email without
        addressing them.

        The name to sign the email with is "Alex Carpenter".

        ## Your traits

        - Show genuine empathy and interest in their situation
        - You are trying to find ways to help them be successful in
          their application
        - You are helpful and friendly
        - You are ensuring they are aware of all strict requirements,
          especially being a South African Citizen, being able to prove
          access to funds, and having the ability to pass an IELTS test
          or have an exemption.
        - You ask clarifying questions when applicable, especially when
          it is unclear if they meet the strict requirements

        ## The questions and their answers that you have been provided.

        {question_and_answers}

        ## Email transcript

        {transcript}

        ## Required email format

        Email subject:

        {subject}

        Email body:

        [Email introduction]

        ---

        Q: [Question 1]
        A: [Answer 1]

        Q: [Question 2]
        A: [Answer 2]

        ...

        Q: [Question N]
        A: [Answer N]

        ---

        [Email conclusion]

        ## Your email response

        Email subject:

        {subject}

        Email body:
    """
).strip()


async def write_and_send_email_response(hash_digest: str, email: Email):
    scope = f'{hash_digest} - {email["user_email"]}'

    email_thread = get_email_thread(email=email)

    if email["subject"].startswith("Fwd: ") or email["subject"].startswith("FW: "):
        subject = email["subject"].removeprefix("Fwd: ").removeprefix("FW: ")

        last_message_lower = email_thread[-1].lower()

        first_reply_line = email["plain_replies_only"].splitlines()[0]
        if first_reply_line.startswith("From: "):
            text_to_extract_reply_to_from = first_reply_line

        else:
            try:
                text_to_extract_reply_to_from = last_message_lower.split(
                    "forwarded message"
                )[-1]

            except ValueError:
                text_to_extract_reply_to_from = email["from"]
    else:
        text_to_extract_reply_to_from = email["from"]
        subject = None

    reply_to = get_cleaned_email(text_to_extract_reply_to_from)

    if reply_to.lower() in {
        "pathways@jims.international",
        "cameron.richardson@ac.edu.au",
    }:
        log_info(
            scope,
            "FAQ would be sent through to pathways itself. Breaking the loop. Doing nothing.",
        )
        return

    if "unsubscribe" in email["subject"].lower():
        log_info(
            scope,
            "Ignoring email that has unsubscribe within the subject.",
        )
        return

    if not email["plain_all_content"].strip():
        response = "The email provided to the agent was empty"
    else:
        response = await _handle_email_body(
            scope=scope,
            email=email,
            email_thread=email_thread,
            reply_to=reply_to,
        )

    log_info(scope, response)

    reply = create_reply(original_email=email, response=response)
    if subject is None:
        subject = reply["subject"]

    subject_with_action_flag = f"{SUPERVISION_SUBJECT_FLAG} {subject}"

    formatting_reply_to = (
        f'reply-formatter==={reply_to.replace("@", "==")}@{ROOT_DOMAIN}'
    )

    postal_data = {
        "from": f"jims-ac-faq@{ROOT_DOMAIN}",
        "to": ["pathways@jims.international"],
        "bcc": ["me@simonbiggs.net"],
        "reply_to": formatting_reply_to,
        "subject": subject_with_action_flag,
        "html_body": reply["html_reply"],
    }

    await send_email(scope, postal_data)


async def _handle_email_body(scope, email: Email, email_thread: list[str], reply_to):
    questions_and_contexts = await extract_questions(email=email)

    questions_without_answers = [
        item
        for item in questions_and_contexts
        if (item["answer_again"] or not item["answer"]) and item["question"]
    ]

    first_name = await get_first_name(
        scope=scope, email_thread=email_thread, their_email_address=reply_to
    )

    response = await _handle_questions(
        scope, email, email_thread, first_name, questions_without_answers
    )

    return response


async def _handle_questions(
    scope, email: Email, email_thread: list[str], first_name, questions
):
    if len(questions) == 0:
        return "No questions were found that require answering"

    faq_data = await load_faq_data()

    coroutines = []
    for question_and_context in questions:
        coroutines.append(
            write_answer(
                scope=scope,
                faq_data=faq_data,
                question_and_context=question_and_context,
            )
        )

    answers = await asyncio.gather(*coroutines)

    question_and_answers_string = ""
    for question_and_context, answer in zip(questions, answers):
        question_and_answers_string += (
            f"Q: {question_and_context['question']}\nA: {answer}\n\n"
        )

    question_and_answers_string = question_and_answers_string.strip()

    prompt_subject = email["subject"]

    if not prompt_subject.startswith("Re:"):
        prompt_subject = f"Re: {prompt_subject}"

    prompt = PROMPT.format(
        transcript="{transcript}",
        question_and_answers=question_and_answers_string,
        first_name=first_name,
        subject=prompt_subject,
    )

    response, _ = await completion_on_thread_with_summary_fallback(
        scope=scope,
        prompt=prompt,
        email_thread=email_thread,
        api_key=OPEN_AI_API_KEY,
        **MODEL_KWARGS,
    )

    return response
