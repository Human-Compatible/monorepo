# Copyright (C) 2022 Simon Biggs

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uvicorn
from fastapi import FastAPI

from assistance import _ctx, _logging

from . import contact_form, email, stripe

_logging.main()

app = FastAPI()

app.include_router(stripe.router)
app.include_router(email.router)
app.include_router(contact_form.router)


@app.on_event("startup")
async def startup_event():
    _ctx.open_session()


@app.on_event("shutdown")
async def shutdown_event():
    await _ctx.close_session()


def main():
    uvicorn.run("assistance._api.main:app", port=8000, log_level="info", reload=True)


if __name__ == "__main__":
    main()
