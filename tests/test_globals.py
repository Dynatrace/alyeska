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

PYTHON_JOB1_SECRET_NAME = "/CI/analytics/RedShiftServer/cicore/pyjob1"
