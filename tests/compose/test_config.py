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
"""Test the compose submodule
"""

import pytest

from alyeska.compose.config import (
    validate_config,
    parse_upstream_dependencies,
    parse_config,
    parse_tasks,
)

from test_compose_globals import (
    COMPOSE_SMALL,
    COMPOSE_BIG,
    COMPOSE_CYCLE,
    COMPOSE_TRICKY,
)


def test__parse_compose_small():
    actual = parse_config(COMPOSE_SMALL)
    expected = {
        "version": "2019.8.21",
        "conda-envs": ["base", "ci-python36-2.1", "python36-2019.8.14"],
        "tasks": {
            "numbers": {"loc": "db/numbers/main.py", "env": "ci-python36-2.1"},
            "calendar": {"loc": "db/calendar/main.py", "env": "ci-python36-2.1"},
            "time_period": {
                "loc": "db/time_period/main.py",
                "env": "ci-python36-2.1",
                "uses": ["numbers", "calendar"],
            },
        },
    }
    assert actual == expected


def test__parse_compose_tricky():
    actual = parse_config(COMPOSE_TRICKY)
    expected = {
        "version": "2019.8.21",
        "conda-envs": ["base", "ci-python36-2.1", "python36-2019.8.14"],
        "tasks-dir": "/workspaces/ci-python/src/cdh",
        "entrypoint": "main.py",
        "tasks": {
            "agent_history": {"loc": "agent_history", "env": "ci-python36-2.1"},
            "application_history": {
                "loc": "application_history",
                "env": "ci-python36-2.1",
            },
        },
    }
    assert actual == expected


@pytest.mark.parametrize(
    "compose_yaml", [COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE, COMPOSE_TRICKY]
)
def test__parse_tasks(compose_yaml):
    config = parse_config(compose_yaml)
    task_map = parse_tasks(config)
    assert len(task_map) > 0


def test__parse_upstream_dependencies():
    config = parse_config(COMPOSE_SMALL)
    actual = parse_upstream_dependencies(config)

    task_map = parse_tasks(config)

    calendar = task_map["calendar"]
    numbers = task_map["numbers"]
    time_period = task_map["time_period"]
    expected = {time_period: {calendar, numbers}}

    assert actual == expected
