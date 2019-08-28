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
"""alyeska.sqlagent tests
"""
from collections import OrderedDict
import os
import pathlib
from typing import Tuple

import pandas as pd
import pytest

import alyeska.locksmith as ls
from alyeska.locksmith.redshift import connect_with_environment
import alyeska.sqlagent as sa

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


def test_input__find_sql_files(tmpdir):
    tmpdir = pathlib.Path(tmpdir)

    files = [f for f in sa.find_sql_files(tmpdir)]
    assert len(files) == 0

    (tmpdir / "another_temp_dir").mkdir()
    files = [f for f in sa.find_sql_files(tmpdir)]
    assert len(files) == 0


def test_output__find_sql_files(tmpdir):
    sql1, sql2, sql3, _ = make_dummy_dir(tmpdir)
    files = [f for f in sa.find_sql_files(tmpdir)]
    assert sql1 in files
    assert sql2 in files
    assert sql3 in files


def test_output__plan_tasks__flat_dir(tmpdir):
    sql1, sql2, sql3, _ = make_dummy_dir(tmpdir)
    files = sa.plan_tasks(tmpdir)
    assert files == [sql1, sql2, sql3]


def test_output__plan_tasks__nested_dir(tmpdir):
    a2 = pathlib.Path(tmpdir) / "a" / "2.sql"
    b1 = pathlib.Path(tmpdir) / "b" / "1.sql"
    a2.parent.mkdir(exist_ok=True, parents=True)
    a2.touch()
    b1.parent.mkdir(exist_ok=True, parents=True)
    b1.touch()

    expected = [b1, a2]
    actual = sa.plan_tasks(tmpdir)
    assert expected == actual


@pytest.mark.timeout(3)
def test_output__execute_tasks(tmpdir):
    sql1, sql2, sql3, _ = make_dummy_dir(tmpdir)
    cnxn = connect_with_environment(ALYESKA_REDSHIFT_SECRET)
    sa.execute_tasks(cnxn, sql1, sql2, sql3)

    expectation = [1, 2, 3, 4, 5, 6]
    result = pd.read_sql("SELECT id FROM temp_alyeska ORDER BY id", cnxn)["id"].tolist()
    assert result == expectation


@pytest.mark.timeout(3)
def test_output__process_batch(tmpdir):
    make_dummy_dir(tmpdir)
    cnxn = connect_with_environment(ALYESKA_REDSHIFT_SECRET)

    sa.process_batch(cnxn, tmpdir)

    expectation = [1, 2, 3, 4, 5, 6]
    result = pd.read_sql("SELECT id FROM temp_alyeska ORDER BY id", cnxn)["id"].tolist()
    assert result == expectation


@pytest.mark.timeout(3)
def test_input__run_subtasks(tmpdir):
    cnxn = connect_with_environment(ALYESKA_REDSHIFT_SECRET)
    p = pathlib.Path(tmpdir)
    sql1, sql2, sql3, txt = make_dummy_dir(p)
    subtasks = OrderedDict({sql1: "sql1", sql2: "sql2", sql3: "sql3", txt: "txt"})

    with pytest.raises(ValueError):
        sa.run_subtasks(cnxn, subtasks)


@pytest.mark.timeout(3)
def test_output__run_subtasks(tmpdir):
    cnxn = connect_with_environment(ALYESKA_REDSHIFT_SECRET)
    p = pathlib.Path(tmpdir)
    sql1, sql2, sql3, _ = make_dummy_dir(p)
    subtasks = OrderedDict({sql1: "sql1", sql2: "sql2"})

    sa.run_subtasks(cnxn, subtasks)
    assert not pd.read_sql("SELECT id FROM temp_alyeska", cnxn).empty


def test_output__gather_subtasks(tmpdir):
    expected = OrderedDict(
        {
            "c": "A log message that spans an entire 79 character line",
            "b": "A log message that spans an entire 79 character line",
            "a": "A log message that spans an entire 79 character line",
        }
    )

    actual = sa.gather_subtasks(dict(expected))
    assert isinstance(actual, OrderedDict)
    assert actual == expected
