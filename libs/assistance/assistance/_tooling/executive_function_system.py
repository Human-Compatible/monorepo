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

# Prompt inspired by the work provided under an MIT license over at:
# https://github.com/hwchase17/langchain/blob/ae1b589f60a/langchain/agents/conversational/prompt.py#L1-L36

import json
import re
import textwrap
from datetime import datetime
from typing import Any, TypedDict
from zoneinfo import ZoneInfo

from assistance import _ctx
from assistance._config import ROOT_DOMAIN, SIMPLER_OPENAI_MODEL
from assistance._email.reply import create_reply, get_all_user_emails
from assistance._keys import get_openai_api_key, get_serp_api_key
from assistance._logging import log_info
from assistance._mailgun import send_email
from assistance._openai import get_completion_only
from assistance._types import Email

from .._summarisation.thread import run_with_summary_fallback

OPEN_AI_API_KEY = get_openai_api_key()
SERP_API_KEY = get_serp_api_key()


MODEL_KWARGS = {
    "engine": SIMPLER_OPENAI_MODEL,
    "max_tokens": 512,
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

PROMPT = textwrap.dedent(
    """
        # Your Purpose

        You are an Executive Function System for an AI cluster. You are
        provided with a task that other AI systems are going to execute,
        and it is your job to select at least 3 tools along with their
        corresponding inputs that can help them be successful in their
        task.


        # Your Available Tools

        Here are the tools available to your cluster:

        def internet_search('<string query>')
            \"""This returns a web search result for the given string argument.\"""

        def now()
            \"""This returns the current date and time.

            This tool takes no input args. Provide only an empty list
            for the args for this tool.
            \"""

        {extra_tools}

        # The task for the AI cluster

        {task}


        # Response Requirements

        - Your response must be valid JSON. It must be a list of at least 3
          dictionaries, with the keys "id",
          "step_by_step_thought_process", "tool", "args", "score", and
          "confidence".
        - Before writing any lines of the JSON you validate that what
          you are about to write is valid JSON.
        - Do not include comments in the JSON response, as that is not
          valid JSON.

        # Example response format for tools. You MUST provide at least 3 tools.

        {example_tool_use}
        {previous_tool_iterations}{optional_previous_results_text}
        # Your JSON Response (MUST be valid JSON, do not include comments)
    """
).strip()


EXAMPLE_TOOL_USE = textwrap.dedent(
    """
        [
            {{
                "id": 0,
                "step_by_step_thought_process": "I will start by using the 'now' tool to get the current date and time.",
                "tool": "now",
                "args": [],
                "score": 9,
                "confidence": 8
            }},
            {{
                "id": 1,
                "step_by_step_thought_process": "There was a query about the Holbrook Cryonics facility. I'm going to do an internet search for that.",
                "tool": "internet_search",
                "args": ["Holbrook Cryonics facility"],
                "score": 9,
                "confidence": 8
            }},
            {{
                "id": 2,
                "step_by_step_thought_process": "The user asked what @phirho's preferred name was, let's search the 'phirho_memory' database for that.",
                "tool": "ai_embeddings_search",
                "args": ["phirho_memory", "phirho's preferred name"],
                "score": 8,
                "confidence": 7
            }},
            {{
                "id": 3,
                "step_by_step_thought_process": "I want to make sure what I am saying is said in a way that is similar to how Philip would say it if it was him, so I will use the 'philip_rhoades_memory' database to search for that.",
                "tool": "ai_embeddings_search",
                "args": ["philip_rhoades_memory", "Responding to a being asked what your preferred name is."],
                "score": 9,
                "confidence": 5
            }},
            {{
                "id": 4,
                "step_by_step_thought_process": "The user also asked how old I was, to do that I need to determine on what date I was born from my memory, and then I need to pass that through to the Python function.",
                "tool": "ai_embeddings_search",
                "args": ["phirho_memory", "phirho's birth date"],
                "score": 9,
                "confidence": 5
            }}
        ]
    """
).strip()


EXTRA_TOOLS = textwrap.dedent(
    """
        def python("<any python expression>")
            \"""This allows you to evaluate expressions using python.

            Only the Python standard library is available to you within
            this tool. It is running within a WASI sandbox and does not
            have any network or file access.
            \"""

        def ai_embeddings_search('<database_name>', '<text to search for within the database>')
            \"""This allows you to search a range of AI embeddings
            databases for the given string argument.

            The current supported databases are:
            - 'philip_rhoades_memory'
            - 'phirho_memory'
            - 'discourse_history'

            \"""
    """
).strip()


class AiToolRequest(TypedDict):
    id: int
    step_by_step_thought_process: str
    tool: str
    args: list[str]
    score: int
    confidence: int

    # TODO: Maybe change this
    result: str


FAILED_ATTEMPT_TEMPLATE = textwrap.dedent(
    """
        # Previous attempt

        You previously submitted the following JSON tools request:

        {previous_request}

        But it resulted in the following error message:

        {error_message}

        Please try again.
    """
).strip()


PREVIOUS_RESULTS_TEMPLATE = textwrap.dedent(
    """
        # Previous iterations of this executive function system has given the following results

        {tools_string}

        For your remaining tools please start your index at {next_index}.
    """
).strip()


async def get_tools_and_responses(
    scope: str,
    task: str,
    email_thread: list[str],
    number_of_tools: int = 3,
    previous_results: None | list[AiToolRequest] = None,
    example_tool_use=EXAMPLE_TOOL_USE,
    extra_tools=EXTRA_TOOLS,
):
    optional_previous_results_text = ""
    if previous_results is not None:
        tools_string = json.dumps(previous_results, indent=2)
        previous_tool_iterations = (
            "\n"
            + PREVIOUS_RESULTS_TEMPLATE.format(
                tools_string=tools_string, next_index=len(previous_results)
            )
            + "\n"
        )
    else:
        previous_tool_iterations = ""

    while True:
        prompt = PROMPT.format(
            task=task,
            transcript="{transcript}",
            optional_previous_results_text=optional_previous_results_text,
            number_of_tools=number_of_tools,
            previous_tool_iterations=previous_tool_iterations,
            example_tool_use=example_tool_use,
            extra_tools=extra_tools,
        )

        response, _ = await run_with_summary_fallback(
            scope=scope,
            prompt=prompt,
            email_thread=email_thread,
            api_key=OPEN_AI_API_KEY,
            **MODEL_KWARGS,
        )

        try:
            tools, number_of_new_tools_to_run = await _evaluate_tools(scope, response)
        except Exception as e:
            optional_previous_results_text = (
                "\n"
                + FAILED_ATTEMPT_TEMPLATE.format(
                    previous_request=response, error_message=str(e)
                )
                + "\n"
            )

            continue

        break

    if number_of_new_tools_to_run > 0:
        tools = await get_tools_and_responses(
            scope=scope,
            task=task,
            email_thread=email_thread,
            number_of_tools=number_of_new_tools_to_run,
            previous_results=tools,
        )

    log_info(
        scope=scope, message=f"Tools with their results: {json.dumps(tools, indent=2)}"
    )

    return tools


async def _evaluate_tools(scope, response):
    try:
        tools: list[AiToolRequest] = json.loads(response)
    except json.JSONDecodeError:
        raise ValueError(f"Response is not valid JSON: {response}")

    number_of_new_tools_to_run = 0

    for tool in tools:
        tool_name = tool["tool"]
        tool_args = tool["args"]
        args = [scope] + tool_args

        try:
            if tool_name == "iterate_executive_function_system":
                number_of_new_tools_to_run = max(number_of_new_tools_to_run, args[0])

                continue

            tool["result"] = await TOOLS[tool_name](*args)
        except KeyError:
            pass
        except Exception as e:
            raise ValueError(
                scope, f"Error running tool `{tool_name}` with args {tool_args}: {e}"
            )

    return tools, number_of_new_tools_to_run


async def _run_search(scope: str, query):
    params = {
        "location": "New+South+Wales,+Australia",
        "hl": "en",
        "gl": "au",
        "google_domain": "google.com.au",
        "q": query,
        "api_key": SERP_API_KEY,
    }

    url = "https://serpapi.com/search"

    response = await _ctx.session.get(url=url, params=params)

    results = await response.json()

    log_info(scope, json.dumps(results, indent=2))

    organic_results = results["organic_results"]

    snippets = []
    for item in organic_results:
        if "snippet" in item:
            snippets.append(item["snippet"])

    return " ".join(snippets)


async def _not_implemented(*args, **kwargs):
    return "Tool not yet implemented"


async def _get_current_date_and_time(*args, **kwargs):
    return datetime.now(tz=ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d %H:%M:%S")


TOOLS = {
    "internet_search": _run_search,
    "python": _not_implemented,
    "now": _get_current_date_and_time,
    "ai_embeddings_search": _not_implemented,
}
