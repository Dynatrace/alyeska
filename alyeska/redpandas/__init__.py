#!/usr/bin/denv python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright 2019 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""alyeska redpandas module for smoother pandas/redshift functionality
"""

from typing import Coroutine

import pandas as pd
import psycopg2

from alyeska.redpandas.exceptions import MissingTableError


def assert_table_exists(
    cnxn: psycopg2.extensions.connection, schema: str, table: str
) -> None:
    """Check that the table actually exists
    
    Args:
        cnxn (psycopg2.extensions.connection): [description]
        schema (str): [description]
        table (str): [description]
    Raises:
        MissingTableError: If the target schema.table does not exist
    """
    query = (
        "SELECT 1 "
        "FROM information_schema.tables "
        f"WHERE table_schema = '{schema}' "
        f"AND table_name = '{table}';"
    )
    if pd.read_sql(query, cnxn).empty:
        raise MissingTableError(f"{schema}.{table} does not exist")


def generate_insert_queries(
    curs: psycopg2.extensions.cursor,
    insert_table: str,
    df: pd.DataFrame,
    *,
    chunksize: int = 10000,
) -> Coroutine:
    """Generator that helps insert_pandas_into. Assumes totally valid 
    arguments, and colnames must match the schema of the insert table.

    Args:
        curs (psycopg2.extensions.cursor): Connection used to insert to table
        insert_table (str): Target table in database
        df (pd.DataFrame): Pandas dataframe that will be inserted
        chunksize (int, optional): How many rows to write per insert.
            Defaults to 10000.

    Returns:
        None
    """
    # TODO: assert cursor here
    if not isinstance(insert_table, str):
        raise TypeError("insert_table must be a str")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(chunksize, int):
        raise TypeError("chunksize must be an int")

    ncol = len(df.columns)
    colnames = df.columns.tolist()
    sanitized_colnames = [f'"{col}"' for col in colnames]

    insert_template = "\n".join(
        [
            f"INSERT INTO {insert_table} ",
            "(",
            # indent the first colname
            "  " + ",\n  ".join(sanitized_colnames),
            ")",
            "VALUES\n",
            "{}",
        ]
    )
    all_values = df.values.tolist()

    formatting = ", ".join(["%s"] * ncol)  # e.g. '%s, %s, %s'
    for i in range(0, len(all_values) + chunksize, chunksize):
        subset_values = all_values[i : i + chunksize]
        if subset_values:
            # as of 2018 Dec 7, you can only use mogrify with a cursor object
            query_values = "  " + ",\n  ".join(
                curs.mogrify(f"({formatting})", row).decode() for row in subset_values
            )
            # cleanup values
            query_values = query_values.replace("'NaT'::timestamp", "NULL")
            query_values = query_values.replace("'NaN'::float", "NULL")
            query_values = query_values.replace("'None'", "NULL")
            query = insert_template.format(query_values)
            yield query


def insert_pandas_into(
    cnxn: psycopg2.extensions.connection,
    insert_table: str,
    df: pd.DataFrame,
    *,
    chunksize: int = 10000,
) -> None:
    """Open connection and insert df into insert_table.

    Args:
        cnxn (psycopg2.extensions.connection): Connection used to insert to table
        insert_table (str): Target table in database
        df (pd.DataFrame): Pandas dataframe that will be inserted
        chunksize (int, optional): How many rows to write per insert.
            Defaults to 10000.

    Returns:
        None: [description]
    """
    if not isinstance(cnxn, psycopg2.extensions.connection):
        raise TypeError("cnxn must be a psycopg2 connection")
    if not isinstance(insert_table, str):
        raise TypeError("insert_table must be a str")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(chunksize, int):
        raise TypeError("chunksize must be an int")

    # TODO: assert insert_table exists
    try:
        schema, table = insert_table.split(".")
    except ValueError:
        # not enough values to unpack e.g. temp_table
        pass
    else:
        assert_table_exists(cnxn, schema, table)

    with cnxn.cursor() as curs:
        for query in generate_insert_queries(
            curs=curs, insert_table=insert_table, df=df, chunksize=chunksize
        ):
            curs.execute(query)

    return None
