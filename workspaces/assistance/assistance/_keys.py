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

import functools

from assistance._paths import SECRETS


def get_openai_api_key():
    return _load_secret("openai-api-key")


def get_postal_api_key():
    return _load_secret("postal-api-key")


def get_stripe_webhook_key():
    return _load_secret("stripe-webhook-key")


@functools.cache
def _load_secret(name: str) -> str:
    secret_path = SECRETS / name

    with open(secret_path, encoding="utf8") as f:
        secret = f.read().strip()

    return secret
