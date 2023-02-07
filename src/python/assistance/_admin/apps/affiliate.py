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

import streamlit as st

from assistance._admin import categories
from assistance._keys import get_jwt_key

CATEGORY = categories.ADMIN
TITLE = "Affiliate Links"


async def main():
    email = st.text_input(
        "Email address of the affiliate who is bein associated with this link"
    )
    details = st.text_area(
        "Details to encode within the affiliate link token (optional)"
    )

    affiliate_link_data = {
        "type": "affiliate",
        "email": email,
        "details": details,
    }
