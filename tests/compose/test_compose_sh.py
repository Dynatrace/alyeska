"""Test the compose-sh functionality
"""
import os
import pathlib

import pytest

from alyeska.compose.compose_sh import convert_yaml_to_sh

from test_compose_globals import COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE


def test__convert_yaml_to_sh():
    actual = convert_yaml_to_sh(COMPOSE_SMALL)
    assert isinstance(actual, str)
