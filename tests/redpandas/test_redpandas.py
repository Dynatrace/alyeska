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
"""Tests for the alyeska.pandas submodule.

Tests will fail if you don't have valid AWS credentials exported to your dev
environment.
"""
import os

import pandas as pd
import pytest

import alyeska as aly
import alyeska.locksmith.redshift as rs
import alyeska.redpandas as rp

ALYESKA_REDSHIFT_SECRET = os.getenv("ALYESKA_REDSHIFT_SECRET")


def test_input__assert_table_exists():
    cnxn = rs.connect_with_environment(ALYESKA_REDSHIFT_SECRET)

    with pytest.raises(TypeError):
        rp.assert_table_exists("etl", "account")

    with pytest.raises(TypeError):
        rp.assert_table_exists("etl", "account", cnxn=cnxn)

    with pytest.raises(rp.MissingTableError):
        cnxn = rs.connect_with_environment(ALYESKA_REDSHIFT_SECRET)
        rp.assert_table_exists(cnxn, "bad_schema", "bad_table")


def test_output__assert_table_exists():
    cnxn = rs.connect_with_environment(ALYESKA_REDSHIFT_SECRET)
    rp.assert_table_exists(cnxn, "etl", "account")


def test__insert_pandas_into():
    cnxn = rs.connect_with_environment(ALYESKA_REDSHIFT_SECRET)
    expected_len = 3
    expected_df = pd.DataFrame({"a": range(expected_len), "c": range(expected_len)})

    table_name = "temp_test"
    aly.sqlagent.execute_sql(
        cnxn, f"CREATE TEMP TABLE {table_name}(a INT, b INT, c INT);"
    )
    rp.insert_pandas_into(cnxn, table_name, expected_df)
    actual_df = pd.read_sql(f"SELECT * FROM {table_name}", cnxn)

    test_result = pd.merge(expected_df, actual_df, on=["a", "c"], how="inner")
    assert len(test_result) == expected_len

    aly.sqlagent.execute_sql(cnxn, f"DROP TABLE {table_name};")
