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
"""Unit tests for the DAG class."""

from collections import defaultdict
import os
import pathlib

import pytest

from alyeska.compose import Task, DAG
from alyeska.compose.exceptions import CyclicGraphError

from test_compose_globals import (
    COMPOSE_SMALL,
    COMPOSE_BIG,
    COMPOSE_CYCLE,
    COMPOSE_TRICKY,
)

# ----------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------


def get_two_tasks():
    return (Task("A.py", env="test-env"), Task("B.py", env="test-env"))


# ----------------------------------------------------------------------------
# DAG magic methods
# ----------------------------------------------------------------------------


def test__validate_dependency():
    make_tea = Task("make_tea.py", "test-env")
    drink_tea = Task("drink_tea.py", "test-env")

    with pytest.raises(TypeError):
        DAG.validate_dependency([1, 2, 3])

    with pytest.raises(ValueError):
        DAG.validate_dependency(defaultdict(set, {make_tea: [drink_tea]}))

    with pytest.raises(ValueError):
        DAG.validate_dependency({Task: {1, 2, 3}})

    DAG.validate_dependency({make_tea: drink_tea})
    DAG.validate_dependency({make_tea: {drink_tea, drink_tea}})


def test__DAG_init():
    DAG()

    # init with dependencies
    make_tea = Task("make_tea.py", "test-env")
    drink_tea = Task("drink_tea.py", "test-env")

    dag = DAG(tasks=make_tea)
    assert len(dag.tasks) == 1

    dag = DAG(tasks={drink_tea, make_tea})
    assert len(dag.tasks) == 2

    dag = DAG(upstream_dependencies={drink_tea: make_tea})
    assert len(dag.tasks) == 2

    dag = DAG(downstream_dependencies={make_tea: drink_tea})
    assert len(dag.tasks) == 2


def test__DAG_repr():
    p = pathlib.Path("make_tea.py")
    make_tea = Task(p, "test-env")
    dag = DAG()
    dag.add_task(make_tea)
    assert repr(dag) == "".join(["DAG({Task(", p.resolve().as_posix(), ")})"])


# ----------------------------------------------------------------------------
# DAG.tasks
# ----------------------------------------------------------------------------
def test__DAG_add_task():
    A, B = get_two_tasks()

    dag = DAG()
    dag.add_task(A)

    assert dag.tasks == {A}, "Test Task was not added to the DAG"


def test__DAG_add_tasks():
    A, B = get_two_tasks()
    C = Task("C.py")
    dag = DAG()
    dag.add_tasks({A, B})

    assert dag.tasks == {A, B}, "Test Tasks were not added to the DAG"

    dag.add_tasks(C)

    assert dag.tasks == {A, B, C}


def test__DAG_remove_task():
    A, B = get_two_tasks()

    dag = DAG()
    dag.add_tasks({A, B})
    dag.remove_task(A)

    assert dag.tasks == {B}


def test__DAG_remove_tasks():
    A, B = get_two_tasks()
    C = Task("C.py")
    dag = DAG()
    dag.add_tasks({A, B, C})
    dag.remove_tasks({A, B})
    assert dag.tasks == {C}

    dag.remove_tasks(C)
    assert dag.tasks == set()


# ----------------------------------------------------------------------------
# add dependencies
# ----------------------------------------------------------------------------
def test__DAG_add_dependency():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, A)
    assert dag._edges[A] == set([B])


def test__DAG_add_dependency_detect_cycle():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, A)
    with pytest.raises(CyclicGraphError):
        dag.add_dependency(A, B)


def test__DAG_add_dependencies():
    A, B = get_two_tasks()
    C = Task("C.py", env="test-env")
    dag = DAG()
    dag.add_dependencies({B: A})
    assert dag._edges[A] == set([B])

    dag = DAG()
    dag.add_dependencies({C: {A, B}})
    assert dag._edges[A] == set([C])
    assert dag._edges[B] == set([C])


def test__DAG_add_dependency_detect_cycle2():
    A, B = get_two_tasks()
    C = Task("C.py", env="test-env")

    dag = DAG()
    with pytest.raises(CyclicGraphError):
        dag.add_dependencies({A: C, B: A, C: B})


# ----------------------------------------------------------------------------
# methods
# ----------------------------------------------------------------------------
def test__DAG_get_downstream():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, depends_on=A)
    assert dag.get_downstream() is not None
    assert dag.get_downstream()[A] == {B}
    assert dag.get_downstream() == {A: {B}}, "Task B is not downstream"


def test__DAG_get_upstream():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, depends_on=A)
    assert dag.get_upstream() is not None
    assert dag.get_upstream()[B] == {A}
    assert dag.get_upstream() == {B: {A}}, "Task A is not upstream"


def test__DAG_get_sources():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, depends_on=A)
    assert dag.get_sources() is not None
    assert dag.get_sources() == {A}


def test__DAG_get_sinks():
    A, B = get_two_tasks()
    dag = DAG()
    dag.add_dependency(B, depends_on=A)
    assert dag.get_sinks() is not None
    assert dag.get_sinks() == {B}


def test__DAG_is_cyclic():
    A, B = get_two_tasks()
    dag = DAG()

    dag.add_dependency(B, depends_on=A)
    assert not dag.is_cyclic(), "acyclic graph idenfied as cyclic"

    with pytest.raises(CyclicGraphError):
        dag.add_dependency(A, depends_on=B)


def test__DAG_from_yaml():
    DAG.from_yaml(COMPOSE_SMALL)

    with pytest.raises(CyclicGraphError):
        DAG.from_yaml(COMPOSE_CYCLE)

    dag = DAG.from_yaml(COMPOSE_TRICKY)
    assert len(dag.tasks) > 0
