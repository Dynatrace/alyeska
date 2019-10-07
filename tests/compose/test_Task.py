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
"""Unit tests for the Task class."""

import pathlib

import pytest

from alyeska.compose import Task


def test__Task_init():
    # This looks gross, but it let's you run the test from anywhere
    existent_loc = pathlib.Path(
        *pathlib.Path(__file__).parts[0:-1], "tea-tasks/boil_water.py"
    )
    non_existent_loc = "path/to/file.py"
    good_env = "python"

    with pytest.raises(TypeError):
        Task()

    with pytest.raises(TypeError):
        Task(loc=None, env=good_env)

    with pytest.raises(ValueError):
        Task(loc="", env=good_env)

    with pytest.raises(TypeError):
        Task(loc=existent_loc, env=None)

    with pytest.raises(ValueError):
        Task(loc=existent_loc, env="")

    with pytest.raises(FileNotFoundError):
        Task(loc=non_existent_loc, env=good_env, validate_loc=True)

    # these should run without issue
    Task(loc=non_existent_loc)
    Task(loc=non_existent_loc, env=good_env)
    Task(loc=existent_loc, env=good_env, validate_loc=True)


def test__Task_repr():
    p = pathlib.Path("make_tea.py")
    make_tea = Task(p, "test-env")
    assert repr(make_tea) == f"Task({p.resolve()})"


def test__Task_hash():
    A = Task("test.py", "test-env")
    B = Task("test.py", "test-env")

    assert hash(A) == hash(B)

    A.loc = "new-test.py"

    assert hash(A) != hash(B)


def test__Task_eq():
    A = Task("test.py", "test-env")
    B = Task("test.py", "test-env")

    assert A == B

    A.loc = "new-test.py"

    assert A != B
