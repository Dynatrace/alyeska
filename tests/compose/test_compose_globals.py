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
"""Filenames used by compose module tests
"""
from os.path import dirname as os_path_dirname
from pathlib import Path as pathlib_Path

CONFIG_SAMPLE_DIR = pathlib_Path(os_path_dirname(__file__)) / "config-samples"
COMPOSE_SMALL = CONFIG_SAMPLE_DIR / "compose-small.yaml"
COMPOSE_BIG = CONFIG_SAMPLE_DIR / "compose-big.yaml"
COMPOSE_CYCLE = CONFIG_SAMPLE_DIR / "compose-cycle.yaml"
COMPOSE_TRICKY = CONFIG_SAMPLE_DIR / "compose-tricky.yaml"

TEA_TASKS_DIR = pathlib_Path(os_path_dirname(__file__)) / "tea-tasks"
BOIL_WATER = TEA_TASKS_DIR / "boil_water.py"
POUR_WATER = TEA_TASKS_DIR / "pour_water.py"
PREP_INFUSER = TEA_TASKS_DIR / "prep_infuser.py"
STEEP_TEA = TEA_TASKS_DIR / "steep_tea.py"
