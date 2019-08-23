"""Tests for the alyeska.pandas submodule.

Tests will fail if you don't have valid AWS credentials exported to your dev
environment.
"""
import pandas as pd
import pytest

import alyeska as aly
import alyeska.locksmith.redshift as rs
import alyeska.redpandas as rp

from test_redpandas_globals import PYTHON_JOB1_SECRET_NAME


def test_input__assert_table_exists():
    cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME)

    with pytest.raises(TypeError):
        rp.assert_table_exists("etl", "account")

    with pytest.raises(TypeError):
        rp.assert_table_exists("etl", "account", cnxn=cnxn)

    with pytest.raises(rp.MissingTableError):
        cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME)
        rp.assert_table_exists(cnxn, "bad_schema", "bad_table")


def test_output__assert_table_exists():
    cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME)
    rp.assert_table_exists(cnxn, "etl", "account")


def test__insert_pandas_into():
    cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME)
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
