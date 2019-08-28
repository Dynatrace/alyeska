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
"""Unit tests for the Composer class."""

from collections import defaultdict
import pathlib

import pytest

from alyeska.compose import Task, DAG, Composer
from alyeska.compose.exceptions import EarlyAbortError, CyclicGraphError

from test_compose_globals import COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE


def test__Composer_init_exceptions():
    """Raise expected exceptions
    """
    A = Task("A.py", "test-exe")
    B = Task("B.py", "test-exe")
    C = Task("C.py", "test-exe")

    dag = DAG()
    dag.add_tasks({A, B, C})

    with pytest.raises(TypeError):
        Composer()

    return None


def test__Composer_init():
    """Nothing should break here
    """
    A = Task("A.py", "test-exe")
    B = Task("B.py", "test-exe")
    C = Task("C.py", "test-exe")

    dag = DAG()
    dag.add_tasks({A, B, C})
    dq = Composer(dag)

    return None


def test__Composer_repr():
    p = pathlib.Path("make_tea.py")
    make_tea = Task(p, "test-exe")
    dag = DAG()
    dag.add_task(make_tea)
    dq = Composer(dag)
    assert repr(dq) == "".join(["Composer(DAG({Task(", p.resolve().as_posix(), ")}))"])


def test__Composer_refresh_dag():
    A = Task("A.py", "test-exe")
    B = Task("B.py", "test-exe")
    C = Task("C.py", "test-exe")
    dag = DAG()
    dag.add_tasks({A, B, C})
    dq = Composer(dag)

    tasks = sorted(list(dq.dag.tasks))
    for t in tasks:
        dq.dag.remove_task(t)

    assert dq.dag.tasks == set()

    dq.refresh_dag()

    new_tasks = sorted(list(dq.dag.tasks))
    for t, nt in zip(tasks, new_tasks):
        assert t == nt


def test__Composer_get_task_schedules():
    A = Task("A.py", "test-exe")
    B = Task("B.py", "test-exe")
    C = Task("C.py", "test-exe")
    Z = Task("Z.py", "test-exe")
    dag = DAG()
    dag.add_tasks({A, B, C, Z})
    dag.add_dependencies({B: A, C: B})
    dq = Composer(dag)

    priorities = dq.get_task_schedules()

    testable = {hash(k): v for k, v in priorities.items()}
    assert testable == {hash(A): 1, hash(B): 2, hash(C): 3, hash(Z): 1}


def test__Composer_get_schedules():
    A = Task("A.py", "test-exe")
    B = Task("B.py", "test-exe")
    C = Task("C.py", "test-exe")
    Z = Task("Z.py", "test-exe")
    dag = DAG()
    dag.add_tasks({A, B, C, Z})
    dag.add_dependencies({B: A, C: B})
    dq = Composer(dag)

    priorities = dq.get_schedules()
    testable = {}

    # build a testable result dict
    for k, v in priorities.items():
        new_set = set()
        if isinstance(v, Task):
            testable[k] = set(v)
            continue

        for vi in v:
            new_set.add(hash(vi))
        testable[k] = new_set

    assert testable == {1: {hash(A), hash(Z)}, 2: {hash(B)}, 3: {hash(C)}}


def test__Composer_from_yaml():
    Composer.from_yaml(COMPOSE_SMALL)

    with pytest.raises(CyclicGraphError):
        Composer.from_yaml(COMPOSE_CYCLE)
