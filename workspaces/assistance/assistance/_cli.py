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

# pylint: disable = import-outside-toplevel

import asyncio
import logging

import typer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = typer.Typer()


@app.command()
def api():
    from assistance._api.main import main as _main

    _main()


@app.command()
def tasker():
    from assistance._tasker import main as _main

    _main()


@app.command()
def rerun():
    from assistance import _ctx
    from assistance._email.handler import rerun as _rerun

    loop = asyncio.get_event_loop()

    _ctx.open_session()
    loop.run_until_complete(_rerun())


@app.command()
def faq():
    from assistance._faq.tasker import run_faq_update

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_faq_update())
