# -*- coding: utf-8 -*-
## ---------------------------------------------------------------------------
## Copyright 2019 Dynatrace LLC
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## ---------------------------------------------------------------------------
"""Integration test for the compose-sh script
"""
import pathlib

import pytest

import alyeska.compose.compose_sh as compose_sh

from test_compose_globals import COMPOSE_SMALL


# Makes sure the output file is in this script's directory.
OUTFILE_PATH: pathlib.Path = (pathlib.Path(__file__).parent / "out.sh").resolve()


@pytest.fixture()
def cleanup_output():
    yield
    if OUTFILE_PATH.exists():
        OUTFILE_PATH.unlink()


@pytest.mark.usefixtures("cleanup_output")
def test__main():
    # Setting --no-check since we don't want to check for task file presence. They definitely don't exist.
    compose_sh.main([str(COMPOSE_SMALL), "-o", str(OUTFILE_PATH), "--no-check"])
    assert OUTFILE_PATH.exists()
