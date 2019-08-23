"""Unit tests for the Task class."""

import pathlib

import pytest

from alyeska.compose import Task

from test_compose_globals import COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE


def test__Task_init():
    good_loc = "path/to/file.py"
    good_env = "python"

    with pytest.raises(TypeError):
        Task()

    with pytest.raises(TypeError):
        Task(loc=None, env=good_env)

    with pytest.raises(ValueError):
        Task(loc="", env=good_env)

    with pytest.raises(TypeError):
        Task(loc=good_loc, env=None)

    with pytest.raises(ValueError):
        Task(loc=good_loc, env="")

    # these should run without issue
    Task(loc=good_loc)
    Task(loc=good_loc, env=good_env)


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
