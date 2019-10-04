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
"""Test the compose-sh functionality
"""
from alyeska.compose.compose_sh import init_flags, convert_yaml_to_sh

from test_compose_globals import COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE


def test__convert_yaml_to_sh():
    # The config_file value doesn't matter since we're passing it in explicitly,
    # but we don't want to check for task file presence since they definitely don't exist.
    init_flags(["foo", "--no-check"])
    actual = convert_yaml_to_sh(COMPOSE_SMALL)
    assert isinstance(actual, str)
