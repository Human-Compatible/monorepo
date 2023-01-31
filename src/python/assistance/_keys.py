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


import openai

from assistance._paths import SECRETS


def load_secret(name: str):
    secret_path = SECRETS / name

    with open(secret_path, encoding="utf8") as f:
        secret = f.read().strip()

    return secret


def write_secret(name: str, secret: str):
    SECRETS.mkdir(parents=True, exist_ok=True)

    secret_path = SECRETS / name

    with open(secret_path, "w", encoding="utf8") as f:
        f.write(secret)


def set_openai_api_key():
    openai.api_key = get_openai_api_key()


def get_openai_api_key():
    return load_secret("openai-api-key")


def get_google_search_api_key():
    return load_secret("google-search-api-key")


def get_google_oauth_client_secret():
    return load_secret("google-oauth-client-secret")


def get_serp_api_key():
    return load_secret("serp-api-key")


def get_jwt_key():
    return load_secret("jwt-key")


def get_mailgun_api_key():
    return load_secret("mailgun-api-key")


def get_notion_api_key():
    return load_secret("notion-api-key")
