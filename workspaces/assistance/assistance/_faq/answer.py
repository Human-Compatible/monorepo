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
import random
import textwrap

from assistance._config import GPT_TURBO_SMALL_CONTEXT
from assistance._embeddings import get_top_questions_and_answers
from assistance._keys import get_openai_api_key
from assistance._logging import log_info
from assistance._openai import (
    get_completion_only,
    get_completion_test_for_json_decoding,
)

from .extract_questions import QuestionAndContext
from .sub_questions import get_sub_questions

OPEN_AI_API_KEY = get_openai_api_key()


MODEL_KWARGS = {
    "engine": GPT_TURBO_SMALL_CONTEXT,
    "max_tokens": 512,
    "temperature": 0.7,
}

PROMPT = textwrap.dedent(
    """
        # Answering a prospective student's question

        You have been forwarded an email from Alex Carpenter. A
        prospective student is asking him questions about Jim's
        International Pathway Program. You are happy to help answer any
        questions that the prospective student may have about the Jim's
        International Pathway Program.

        Within their email the prospective student has asked a question.
        You are to draft Alex's answer to the question. Below are a
        range of previous FAQ responses that Alex has provided to other
        students. Use these FAQ responses as a guide to help you draft
        your own response.

        Do not use any of your outside knowledge to help you draft your
        response. Only use the information provided to you within the
        previous FAQ responses. If no FAQ responses is relevant to the
        question, then ONLY respond with an empty string.

        Make sure to focus on the FAQ responses that have the highest
        "Importance Score".

        When writing your response to the question do not include a
        greeting or conclusion. The answer you write here will be
        included along with other questions and answers within an email.
        Do not write that email yourself. Only answer the question.

        ## Your traits

        - Show genuine empathy and interest in their situation
        - You are trying to find ways to help them be successful in
          their application
        - You are helpful and friendly

        ## Question asked by THIS applicant

        {question}

        ## Context from the email transcript for THIS question

        {context}

        ## Previous responses to OTHER prospective students

        These questions are not necessarily the same as the question
        asked by this prospective student.

        {faq_responses}

        ## Your answer

        Question: {question} Answer:
    """
).strip()

RANK = textwrap.dedent(
    """
        # Select best answer

        You have been forwarded an email from Alex Carpenter. A
        prospective student is asking him questions about Jim's
        International Pathway Program. You are happy to help answer any
        questions that the prospective student may have about the Jim's
        International Pathway Program.

        Within their email the prospective student has asked a question.
        You have also been provide with a list of possible answers. You
        are to select the best answer to the question from the list of
        answers.

        You are required to select the answer that both, best answers
        the original question, but also best aligns with the responses
        within the FAQ provided.

        Your response is required to be the id of the answer itself
        ONLY.

        If no response meets the required answers standard then set the
        "does any response meet the required standard?" field to false.

        ## Previous responses to OTHER prospective students

        These questions are not necessarily the same as the question
        asked by this prospective student.

        {faq_responses}

        ## Question asked by THIS applicant

        {question}

        ## Context from the email transcript for THIS question

        {context}

        ## Answers to THIS applicant's question to choose from

        {answers}

        ## Required JSON format

        {{
            "think step by step for id": "<step by step reasoning>",
            "id of the best answer": <id>,
            "think step by step for the four validation checks": "<step by step reasoning>",
            "does the selected answer completely answer the user's question?": <true or false>,
            "does the selected answer get its information from the FAQ responses?": <true or false>,
            "does the selected answer answer the question in a way that is consistent with the FAQ responses?": <true or false>,
            "does the selected answer suggest following up the question with someone else?": <true or false>
        }}

        ## Your JSON response (ONLY respond with JSON, nothing else)
    """
).strip()

MAXIMUM_FAQS = 15
SEED = 42


async def write_answer(
    scope: str,
    faq_data,
    question_and_context: QuestionAndContext,
):
    question = question_and_context["question"]
    context = question_and_context["context"]

    questions = await get_sub_questions(scope=scope, question=question, context=context)

    # Don't need to batch the questions for this use case
    # questions_by_batch = await get_questions_by_batch(scope=scope, questions=questions)

    faq_responses = await get_top_questions_and_answers(
        openai_api_key=OPEN_AI_API_KEY, faq_data=faq_data, queries=questions
    )

    faq_responses = faq_responses[0:MAXIMUM_FAQS]

    sorted_faq_responses = faq_responses.copy()

    deterministic_random = random.Random(SEED)

    coroutines = []
    for _ in range(5):
        coroutines.append(
            _get_completion_with_faq_prune_fallback(
                scope=scope,
                prompt=PROMPT.format(
                    question=question,
                    context=context,
                    faq_responses="{faq_responses}",
                ),
                faq_responses=faq_responses,
            )
        )
        deterministic_random.shuffle(faq_responses)

    question_responses = await asyncio.gather(*coroutines)

    log_info(scope, json.dumps(question_responses, indent=2))

    if "" in question_responses:
        return ""

    question_responses_with_id = []
    for i, response in enumerate(question_responses):
        question_responses_with_id.append({"id": i, "answer": response})

    response = await _get_completion_with_faq_prune_fallback(
        scope=scope,
        prompt=RANK.format(
            question=question,
            context=context,
            faq_responses="{faq_responses}",
            answers=json.dumps(question_responses_with_id, indent=2),
        ),
        faq_responses=sorted_faq_responses,
        check_json=True,
    )

    response_data = json.loads(response)
    best_answer_id = response_data["id of the best answer"]

    all_test_results = [
        response_data[
            "does the selected answer completely answer the user's question?"
        ],
        response_data[
            "does the selected answer get its information from the FAQ responses?"
        ],
        response_data[
            "does the selected answer answer the question in a way that is consistent with the FAQ responses?"
        ],
        not response_data[
            "does the selected answer suggest following up the question with someone else?"
        ],
    ]

    if not all(all_test_results):
        return ""

    best_answer_id = response_data["id of the best answer"]

    return question_responses[int(best_answer_id)]


async def _get_completion_with_faq_prune_fallback(
    scope: str, prompt: str, faq_responses: list[str], check_json=False
):
    if check_json:
        completion_function = get_completion_test_for_json_decoding
    else:
        completion_function = get_completion_only

    while True:
        try:
            return await completion_function(
                scope=scope,
                prompt=prompt.replace("{faq_responses}", "\n\n".join(faq_responses)),
                api_key=OPEN_AI_API_KEY,
                **MODEL_KWARGS,
            )
        except ValueError as e:
            if "Model maximum reached" not in str(e):
                raise e

            if len(faq_responses) == 0:
                raise e

            faq_responses = faq_responses[0:-1]
