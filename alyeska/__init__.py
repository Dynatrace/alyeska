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

"""Alyeska /al-ee-EHS-kah/ n. A Data Pipeline Toolkit

https://github.com/Dynatrace/alyeska

Alyeska, or _Aly_ for short, is a Python toolkit to help manage data pipelines.
Tools are broken out into modules with niche purposes:
    - `compose` is a workflow dependency management tool
    - `locksmith` authorizes AWS sessions and Redshift connections
    - `logging` standardizes logging practices
    - `redpandas` supports less verbose pandas/redshift functionality
    - `sqlagent` supports SQL executation and runtime configuration
"""

from functools import wraps as functools_wraps
from logging import info as logging_info
from pathlib import Path as pathlib_Path
from typing import Callable, Coroutine, Tuple

# load into alyeska namespace to users can have easy access
from alyeska import compose
from alyeska import locksmith
from alyeska import logging
from alyeska import redpandas
from alyeska import sqlagent

__author__ = "Nick Vogt"
__copyright__ = "Copyright 2019, Dynatrace LLC"
__credits__ = ["Colin Patel-Murray"]
__license__ = "Apache v2.0"
__version__ = "0.2.0dev3"
__maintainer__ = "Nick Vogt"
__email__ = "vogt4nick@gmail.com"
__status__ = "Prototype"  # one of "Prototype", "Development", "Production"


def rtap(rel_path: str) -> str:
    """Convert relative path to absolute path

    Args:
        rel_path (str): relative path to be converted

    Returns:
        str: absolute path to file
    """
    assert isinstance(rel_path, str), TypeError("rel_path must be a str")
    current_dir = pathlib_Path(__file__).parent
    rel_path = pathlib_Path(rel_path)
    abs_path = current_dir / rel_path

    return abs_path.resolve()


def find_files(
    root_dir: pathlib_Path, include_subdirs: bool = True
) -> Coroutine[str, None, str]:
    """Find files in the given directory.

    Args:
        root_dir (pathlib_Path): The directory to look for files
        include_subdirs (bool): Whether to include subdirectories in the search

    Returns:
        Coroutine[str]: [description]
    """
    root_dir = pathlib_Path(root_dir)

    def find_toplevel_objects(root_dir: pathlib_Path) -> Coroutine[str, None, str]:
        for child in root_dir.iterdir():
            yield child.resolve()

    for obj in find_toplevel_objects(root_dir):
        if include_subdirs is True and obj.is_dir():
            yield obj
            yield from find_toplevel_objects(obj)
        else:  # don't yield obj twice
            yield obj


def check_environment(env_name: str, allowed: Tuple[str]) -> None:
    """Raise ValueError if invalid environment is selected

    Args:
        env_name (str)
        allowed (Tuple[str]): Which env_name values are permitted

    Raises:
        ValueError: if invalid environment is passed to env_name
    """
    logging_info("Checking environment")

    if not isinstance(env_name, str):
        raise TypeError("`env_name` must be a str")
    if not isinstance(allowed, (list, tuple)):
        raise TypeError("`allowed` must be a list or tuple of strs")
    if not all(isinstance(env, str) for env in allowed):
        raise TypeError("`allowed` must be a list or tuple of strs")

    if env_name in allowed:
        logging_info(f"Using environment: {env_name}")
    else:
        raise ValueError(f"{env_name} not one of {allowed}")
