#!/usr/bin/denv python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright 2019 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""Determine whether a given compose.yaml is valid
"""

from packaging.version import parse as version_parse
from typing import Dict

from alyeska.compose.exceptions import ConfigurationError


def validate_config(config: Dict) -> None:
    """Determine whether a given compose.yaml is valid
    
    Args:
        config (Dict): dict representation of compose.yaml
    
    Raises:
        ConfigurationError
    """
    if not isinstance(config, dict):
        raise ValueError("config must be parsed as a dict before validation")
    validate_top_level(config)
    validate_tasks(config)


# def validate_version(config: Dict) -> None:
#     """Raise error if supplied version is invalid

#     Args:
#         config (Dict): [description]

#     Raises:
#         ConfigurationError: [description]
#         ConfigurationError: [description]

#     Returns:
#         None: [description]
#     """
#     try:
#         version_str = config["version"]
#     except KeyError:
#         raise ConfigurationError("Missing `version` in compose.yaml")

#     try:
#         observed_version = version_parse(version_str)
#     except TypeError:
#         raise ConfigurationError("`version` must be a string")

#     possible_versions = set([version_parse("2019.8.15")])
#     if observed_version not in possible_versions:
#         msg = (
#             f"compose.yaml version {observed_version.base_version} is not "
#             f"supported. Try one of {[v.base_version for v in possible_versions]}"
#         )
#         raise ConfigurationError(msg)


def validate_top_level(config: Dict) -> None:
    required_keys = {"conda-envs", "tasks", "version"}
    optional_keys = {"tasks-dir", "entrypoint"}
    possible_keys = required_keys.union(optional_keys)

    observed_keys = set(config.keys())

    if not required_keys.issubset(observed_keys):
        raise ConfigurationError(
            f"Composer config is missing one or more required tags. "
            f"Observed tags: {observed_keys}. "
            f"Required tags: {required_keys}."
        )
    bad_tags = observed_keys - possible_keys
    if len(bad_tags) > 0:
        raise ConfigurationError(
            f"Composer config contains one or more invalid tags: {bad_tags}"
        )


def validate_tasks(config: Dict) -> None:
    try:
        tasks = config["tasks"]
    except KeyError:
        raise ConfigurationError("config is missing `tasks`")
