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
import pytest

from alyeska.compose import Task, DAG, Composer

from test_compose_globals import COMPOSE_SMALL, COMPOSE_BIG, COMPOSE_CYCLE


def test__readme_example():

    ## define tasks and environments
    pour_water = Task("./tea-tasks/pour_water.py")
    boil_water = Task("./tea-tasks/boil_water.py")
    prep_infuser = Task("./tea-tasks/prep_infuser.py")
    steep_tea = Task("./tea-tasks/steep_tea.py")

    ## define runtime dependencies
    make_tea = DAG(
        upstream_dependencies={
            boil_water: {pour_water},
            steep_tea: {boil_water, prep_infuser},
        }
    )

    ## run tasks
    dq = Composer(make_tea)
    dq.get_schedules()
    # defaultdict(<class 'set'>, {
    #     1: {Task(prep_infuser.py), Task(pour_water.py)},
    #     2: {Task(boil_water.py)},
    #     3: {Task(steep_tea.py)}})


if __name__ == "__main__":
    test__readme_example()
