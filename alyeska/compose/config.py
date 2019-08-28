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
"""alyeska.compose module to assist dependency management
"""

from collections import defaultdict
import logging
import pathlib
from typing import Dict, List, Set

import yaml

from alyeska.compose import Task, DAG, Composer
from alyeska.compose.exceptions import ConfigurationError
from alyeska.compose.validate import validate_config


def parse_config(p: pathlib.Path) -> Dict:
    """Parse the compose.yaml file and return a dict

    Basically the same as yaml.load().

    Args:
        p (pathlib.Path): path to compose.yaml

    Returns:
        Dict: parsed compose.yaml file
    """
    p = pathlib.Path(p)
    config = yaml.load(p.read_text(), Loader=yaml.Loader)

    validate_config(config)

    return config


def parse_tasks(config: Dict) -> Dict[str, Task]:
    """Map task aliases to their Task object representation

    Args:
        config (Dict): compose.yaml as dict

    Returns:
        Dict[str, Task]: Dict mapping task aliases to Task objects
    """
    task_map = {}
    tasks_dir = config.get("tasks-dir")
    entrypoint = config.get("entrypoint")
    for task_name, task_config in config["tasks"].items():
        # ugly but clear if-else chains
        try:
            task_loc = task_config["loc"]
        except KeyError:
            task_loc = task_name

        if tasks_dir and entrypoint:
            path = pathlib.Path(tasks_dir, task_loc, entrypoint)
        elif tasks_dir:
            path = pathlib.Path(tasks_dir, task_loc)
        elif entrypoint:
            path = pathlib.Path(task_loc, entrypoint)
        else:
            path = task_loc
        env = task_config["env"]
        task_map[task_name] = Task(loc=path, env=env)

    return task_map


def parse_upstream_dependencies(config: Dict) -> Dict[Task, Set[Task]]:
    """Map tasks to their upstream dependencies, if any

    Args:
        config (Dict): compose.yaml as dict

    Returns:
        Dict[Task, Set[Task]]: mapping Task objects to their upstream dependencies
    """
    task_map = parse_tasks(config)
    d = defaultdict(set, {})
    for task_name in config["tasks"].keys():
        task_attrs = config["tasks"][task_name]
        try:
            upstream_names = task_attrs["uses"]
        except KeyError:
            pass
        else:
            downstream_task = task_map[task_name]
            if isinstance(upstream_names, str):
                upstream_name = upstream_names
                upstream_task = task_map[upstream_name]
                d[downstream_task].add(upstream_task)
            else:
                for upstream_name in upstream_names:
                    upstream_task = task_map[upstream_name]
                    d[downstream_task].add(upstream_task)

    return d
