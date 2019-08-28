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
"""Test common use cases for the alyeska module
"""
from collections import OrderedDict
import os
import pathlib
from typing import Tuple

import pytest

import alyeska as aly
import alyeska.locksmith as ls
import alyeska.locksmith.redshift as rs

ALYESKA_REDSHIFT_SECRET = os.getenv("ALYESKA_REDSHIFT_SECRET")


def make_dummy_dir(tmpdir: os.path) -> Tuple[pathlib.Path]:
    """construct a dummy directory for tests

    Args:
        tmpdir (os.path)

    Returns:
        Tuple[pathlib.Path]: Tuple of files created
    """
    tmpdir = pathlib.Path(tmpdir)

    sql1 = tmpdir / "01-sample.sql"
    sql1.write_text("CREATE TEMP TABLE temp_alyeska(id INT);")

    sql2 = tmpdir / "02-sample.sql"
    sql2.write_text("INSERT INTO temp_alyeska(id) VALUES (1), (2), (3);")

    sql3 = tmpdir / "03-sample.sql"
    sql3.write_text("INSERT INTO temp_alyeska(id) VALUES (4), (5), (6);")

    txt = tmpdir / "sample.txt"
    txt.write_text("This is a txt file.")

    return (sql1, sql2, sql3, txt)


def test__connect_to_redshift():
    secret_name = ALYESKA_REDSHIFT_SECRET
    aly.locksmith.redshift.connect_with_environment(secret_name)


def test__simple_sql_task(tmpdir):
    sql1, sql2, sql3, _ = make_dummy_dir(tmpdir)

    subtasks = OrderedDict(
        {
            sql1: "A long log message that says we're running the sql1 task",
            sql2: "A long log message that says we're running the sql2 task",
            sql3: "A long log message that says we're running the sql3 task",
        }
    )

    secret_name = ALYESKA_REDSHIFT_SECRET
    cnxn = aly.locksmith.redshift.connect_with_environment(secret_name)

    aly.sqlagent.run_subtasks(cnxn, subtasks)
