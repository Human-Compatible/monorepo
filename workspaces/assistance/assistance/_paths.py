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


import pathlib

LIB = pathlib.Path(__file__).parent

STORE = pathlib.Path.home().joinpath(".assistance")

MONOREPO = LIB.parent.parent.parent
PRIVATE = MONOREPO.joinpath("private")
REFUGE = PRIVATE.joinpath("refuge")

SECRETS = REFUGE.joinpath("secrets")

if not SECRETS.exists():
    SECRETS = STORE.joinpath("secrets")


SYNCED_JIMS_REPO = REFUGE / "jims"
SYNCED_RECORDS = SYNCED_JIMS_REPO / "records"
SYNCED_EMAIL_RECORDS = SYNCED_RECORDS / "emails"
SYNCED_EOI_RECORDS = SYNCED_EMAIL_RECORDS / "eoi"

SYNCED_CONTACT_FORM_RECORDS = SYNCED_EOI_RECORDS / "contact-form-api"
SYNCED_SENT_RECORDS = SYNCED_EMAIL_RECORDS / "sent"
SYNCED_STARTED_APPLICATION = SYNCED_EMAIL_RECORDS / "started-application"
SYNCED_FAQS_STORE = SYNCED_JIMS_REPO.joinpath("faqs.toml")

LOCAL_RECORDS = STORE.joinpath("records")
LOCAL_EMAIL_RECORD = LOCAL_RECORDS.joinpath("emails")

COMPLETION_CACHE = LOCAL_RECORDS.joinpath("completion-cache")

PIPELINES = STORE.joinpath("pipelines")

EMAIL_PIPELINES = PIPELINES.joinpath("emails")
NEW_EMAILS = EMAIL_PIPELINES.joinpath("new")

LOGS = STORE.joinpath("server", "logs")


def get_emails_path(hash_digest: str, create_parent: bool = False):
    path = _get_record_path(LOCAL_EMAIL_RECORD, hash_digest, create_parent)

    return path


def get_contact_form_path(hash_digest: str, create_parent: bool = False):
    path = _get_record_path(SYNCED_CONTACT_FORM_RECORDS, hash_digest, create_parent)

    return path


def get_completion_cache_path(hash_digest: str, create_parent: bool = False):
    path = _get_record_path(COMPLETION_CACHE, hash_digest, create_parent)

    return path


def _get_record_path(root: pathlib.Path, hash_digest: str, create_parent: bool):
    path = root / _get_relative_json_path(hash_digest)

    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    return path


def _get_relative_json_path(hash_digest: str):
    return pathlib.Path(hash_digest[0:4]) / hash_digest[4:8] / f"{hash_digest}.json"
