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
    env_name = os.getenv("ENV_NAME") if os.getenv("ENV_NAME") else "analytics"
    secret_name = f"/CI/{env_name}/RedShiftServer/cicore/pyjob1"
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

    env_name = os.getenv("ENV_NAME") if os.getenv("ENV_NAME") else "analytics"
    secret_name = f"/CI/{env_name}/RedShiftServer/cicore/pyjob1"
    cnxn = aly.locksmith.redshift.connect_with_environment(secret_name)

    aly.sqlagent.run_subtasks(cnxn, subtasks)
