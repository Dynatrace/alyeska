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
import pathlib
from typing import Dict, Set

import yaml

from alyeska.compose import Task
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


def parse_tasks(config: Dict, validate_tasks: bool = False) -> Dict[str, Task]:
    """Map task aliases to their Task object representation

    Args:
        config (Dict): compose.yaml as dict
        validate_tasks (bool, optional): if true, validates that the task file exists

    Returns:
        Dict[str, Task]: Dict mapping task aliases to Task objects
    """
    task_map = {}
    tasks_dir = config.get("tasks-dir")
    entrypoint = config.get("entrypoint")
    for task_name, task_config in config["tasks"].items():
        # potentially unset key
        task_loc = task_config.get("loc", task_name)

        # only task_loc is guaranteed present
        path_components = filter(None, [tasks_dir, task_loc, entrypoint])
        path = pathlib.Path(*path_components)

        env = task_config["env"]
        task_map[task_name] = Task(path, env, validate_tasks)

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
