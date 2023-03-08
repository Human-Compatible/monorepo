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


from assistance._config import ProgressionItem


def get_current_stage_and_task(
    progression_cfg: list[ProgressionItem], complete_progression_keys: set[str]
) -> tuple[str | None, str | None, list[str] | None]:
    for item in progression_cfg:
        if item["key"] in complete_progression_keys:
            continue

        fields_for_completion = None
        if "fields_for_completion" in item:
            fields_for_completion = item["fields_for_completion"]

        return item["key"], item["task"], fields_for_completion

    return None, None, None
