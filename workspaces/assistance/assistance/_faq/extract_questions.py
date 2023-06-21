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
import textwrap
from typing import TypedDict

from assistance._completion.summary import completion_on_thread_with_summary_fallback
from assistance._config import GPT_SOTA
from assistance._email.thread import get_email_thread
from assistance._keys import get_openai_api_key
from assistance._logging import log_info
from assistance._types import Email

OPEN_AI_API_KEY = get_openai_api_key()

MODEL_KWARGS = {
    "engine": GPT_SOTA,
    "max_tokens": 4096,
    "temperature": 0,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


PROMPT = textwrap.dedent(
    """
        # Extraction of Questions about Jim's International Pathway Program

        You have been provided with an email transcript where a range of
        questions about the Jim's International Pathway Program and its
        application process have been asked.

        It is your job to extract a full and complete list of all of the
        questions, queries, as well as any requests for information that
        are within the email transcript that have been asked by the
        sender that used the email address of {email_address}.

        DO NOT include questions that have been asked by the sender
        that used the address of pathways@jims.international.

        Make sure to include any relevant contextual information from
        the email transcript around why the user is asking the question.
        In particular, make sure to include information around the focus
        of the question being asked.

        Include at the end of the context a re-wording of the question
        in your own words. Making sure to highlight any key components
        of the question that you think are important.

        Do not reword the question, provide the question as is it was
        originally written.

        If somewhere within the transcript the question has already been
        answered then provide the answer within the "extracted answer"
        field.

        If the question has not been answered yet, leave the "extracted
        answer" field blank with an empty string ("").

        If there are no questions within the email then the correct JSON
        response is to provide only an empty list ([]).

        ## The email transcript

        {transcript}

        ## Required JSON format

        [
            {
                "think step by step for question and its context": "<step by step reasoning>",
                "question": "<first question>",
                "context": "<any relevant question context from the email transcript>",
                "think step by step for extracted answer": "<step by step reasoning>",
                "extracted answer": "<The answer given in the transcript>",
                "think step by step for verification questions": "<step by step reasoning>",
                "has the user's question been answered?": <true or false>,
                "was this question asked after the given answer?": <true or false>,
                "was this question originally asked by {email_address}?": <true or false>,
                "was this question originally asked by pathways@jims.international?": <true or false>
            },
            {
                "think step by step for question and its context": "<step by step reasoning>",
                "question": "<first question>",
                "context": "<any relevant question context from the email transcript>",
                "think step by step for extracted answer": "<step by step reasoning>",
                "extracted answer": "<The answer given in the transcript>",
                "think step by step for verification questions": "<step by step reasoning>",
                "has the user's question been answered?": <true or false>,
                "was this question asked after the given answer?": <true or false>,
                "was this question originally asked by {email_address}?": <true or false>,
                "was this question originally asked by pathways@jims.international?": <true or false>
            },
            ...
            {
                "think step by step for question and its context": "<step by step reasoning>",
                "question": "<first question>",
                "context": "<any relevant question context from the email transcript>",
                "think step by step for extracted answer": "<step by step reasoning>",
                "extracted answer": "<The answer given in the transcript>",
                "think step by step for verification questions": "<step by step reasoning>",
                "has the user's question been answered?": <true or false>,
                "was this question asked after the given answer?": <true or false>,
                "was this question originally asked by {email_address}?": <true or false>,
                "was this question originally asked by pathways@jims.international?": <true or false>

            }
        ]

        ## Your JSON response (ONLY respond with JSON, nothing else)
    """
).strip()


SUMMARY_INSTRUCTIONS = textwrap.dedent(
    """
        When summarising the email thread, please make sure to include
        any questions that was asked within the email thread as well as
        any answers that were given, as well as any contextual
        information around the question and answer itself.
    """
).strip()


class QuestionAndContext(TypedDict):
    question: str
    context: str
    answer: str
    answer_again: bool


async def extract_questions(email: Email, reply_to: str) -> list[QuestionAndContext]:
    scope = email["user_email"]

    email_thread = get_email_thread(email)

    # last_two_emails_thread = email_thread[-2:]

    response, _ = await completion_on_thread_with_summary_fallback(
        scope=scope,
        test_json=True,
        prompt=PROMPT.replace("{email_address}", reply_to),
        instructions="",
        email_thread=email_thread,
        api_key=OPEN_AI_API_KEY,
        **MODEL_KWARGS,
    )

    log_info(scope, response)

    questions = json.loads(response)

    question_origin_template = "was this question originally asked by {email}?"

    for question in questions:
        question["answer"] = question["extracted answer"]
        del question["extracted answer"]

        question_user_origin_key = question_origin_template.format(email=reply_to)
        question_agent_origin_key = question_origin_template.format(
            email="pathways@jims.international"
        )
        question_was_from_user = (
            question[question_user_origin_key]
            and not question[question_agent_origin_key]
        )

        del question[question_user_origin_key]
        del question[question_agent_origin_key]

        question["answer_again"] = (
            not question["has the user's question been answered?"]
            or question["was this question asked after the given answer?"]
        ) and question_was_from_user

        del question["has the user's question been answered?"]
        del question["was this question asked after the given answer?"]

    return questions
