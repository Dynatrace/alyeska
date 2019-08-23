"""Test the compose submodule
"""
from collections import defaultdict
import os
import pathlib
from pprint import pprint

import pytest
import yaml
from yaml import Loader, Dumper

from alyeska.compose import Task, DAG
from alyeska.compose.exceptions import ConfigurationError, CyclicGraphError
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
