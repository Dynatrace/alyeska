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
"""Similar functionality to SQL Server Agent. Flush with functionality to
automate SQL tasks.
"""

from collections import OrderedDict
import logging
import os
import pathlib
from typing import Tuple, Coroutine, List, Dict
import warnings

import psycopg2

import alyeska as aly
import alyeska.locksmith as ls


def find_sql_files(
    sql_dir: pathlib.Path, include_subdirs: bool = True
) -> Coroutine[pathlib.Path, None, pathlib.Path]:
    """Find SQL files in the given directory.

    Args:
        sql_dir (pathlib.Path): The directory to look for SQL files
        include_subdirs (bool): Whether to include subdirectories in the search

    Returns:
        Coroutine[pathlib.Path, None, pathlib.Path]: [description]
    """
    sql_dir = pathlib.Path(sql_dir)
    for file_or_dir in aly.find_files(sql_dir):
        if file_or_dir.is_file() and file_or_dir.suffix == ".sql":
            yield file_or_dir


def execute_sql(cnxn: psycopg2.extensions.connection, cmd: str) -> None:
    """Open `cnxn` and pass the `cmd` argument.

    ? Should we handle EOF errors?

    Args:
        cnxn (psycopg2.extensions.connection): Connection used to execute command.
        cmd (str): SQL command to be executed.

    Returns:
        None
    """
    if not isinstance(cnxn, psycopg2.extensions.connection):
        raise TypeError("cnxn must be a psycopg2 connection")
    if not isinstance(cmd, str):
        raise TypeError("cmd must be a str")

    with cnxn.cursor() as rs:
        rs.execute(cmd)

    return True


def parametrize_queries(
    query_templates: List[str], param_dicts: List[Dict[str, str]]
) -> Coroutine[str, None, str]:
    """Parametrize queries with the given param dicts.

    Expect len(query_templates) * len(param_dicts) queries.

    Args:
        query_templates (List[str]): Query templates to be parametrized
        param_dicts (List[Dict[str, str]]): mappings used to parametrize query
            templates
    """

    def replace_all(template: str, param_dict: Dict) -> str:
        """Replace patterns in the template with pattern: replacement pairs
        from the param_dict.
        """
        query = template
        for pattern, replacement in param_dict.items():
            query = query.replace(pattern, replacement)

        return query

    count_queries = len(query_templates) * len(param_dicts)
    logging.info(f"Parametrize {count_queries} queries")

    for param_dict in param_dicts:
        for query_template in query_templates:
            formatted_query = replace_all(query_template, param_dict)

            yield formatted_query


def run_queries_sequentially(cnxn: psycopg2.extensions.connection, *queries) -> None:
    """Execute queries in sequence

    Args:
        cnxn (psycopg2.extensions.connection): Database connection
    """
    for query in queries:
        aly.sqlagent.execute_sql(cnxn, query)


def run_queries_sequentially_with_params(
    cnxn: psycopg2.extensions.connection,
    query_templates: List[str],
    param_dicts: List[Dict[str, str]],
) -> None:
    """Parametrize templates and run tasks sequentially

    Args:
        cnxn (psycopg2.extensions.connection): Database connection
        query_templates (List[str]): Query templates to be formatted
        param_dicts (List[Dict[str, str]]): Param mappings used to format
            query templates
    """
    queries = parametrize_queries(query_templates, param_dicts)
    run_queries_sequentially(cnxn, *queries)


# ----------------------------------------------------------------------------
# Deprecated Functions -------------------------------------------------------
# ----------------------------------------------------------------------------


def plan_tasks(sql_dir: pathlib.Path) -> List[pathlib.Path]:
    """Generate an ordered sequence of SQL files.

    Args:
        sql_dir (pathlib.Path): Where to look for SQL files.

    Returns:
        List[pathlib.Path]: An ordered sequence of filepaths.

    Notes:
        plan_tasks doesn't return a generator here because the sorting step
        creates a list. Returning this sorted list as a generator would just
        create computational overhead.
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.plan_tasks is deprecated; "
            "load SQL into memory and arrange tasks manually,"
            "or consider using alyeska.compose"
        ),
        category=DeprecationWarning,
    )
    sql_dir = pathlib.Path(sql_dir)

    return sorted(find_sql_files(sql_dir, include_subdirs=True), key=lambda p: p.name)


def execute_tasks(cnxn: psycopg2.extensions.connection, *tasks: pathlib.Path) -> None:
    """Execute the SQL in each task argument in order

    Args:
        cnxn (psycopg2.extensions.connection): [description]
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.execute_tasks is deprecated; "
            "use alyeska.sqlagent.run_tasks_sequentially"
        ),
        category=DeprecationWarning,
    )
    # assert all tasks are valid before executing them all
    tasks = [pathlib.Path(task) for task in tasks]
    assert all([task.exists() for task in tasks])  # TODO: Raise a meaningful error
    cwd = pathlib.Path.cwd()
    logging.info(f"Excuting SQL tasks in {cwd}")
    for task in tasks:
        logging.info(f"Executing {task.name}")
        execute_sql(cnxn, task.read_text())


def process_batch(cnxn: psycopg2.extensions.connection, sql_dir: pathlib.Path) -> None:
    """Find SQL files in sql_dir and execute as batch process

    Args:
        cnxn (psycopg2.extensions.connection): [description]
        sql_dir (str): [description]

    Returns:
        None: [description]
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.process_batch is deprecated; "
            "load SQL into memory and use "
            "alyeska.sqlagent.run_tasks_sequentially instead"
        ),
        category=DeprecationWarning,
    )
    sql_dir = pathlib.Path(sql_dir)
    tasks = plan_tasks(sql_dir)
    execute_tasks(cnxn, *tasks)


def gather_subtasks(d: Dict) -> OrderedDict:
    """Declare subtasks and log messages in order

    Args:
        d (Dict): a dict-like object mapping subtasks to log messages

    Returns:
        OrderedDict: map tasks to log messages in order of execution
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.gather_subtasks is deprecated; "
            "use built-in collections.OrderedDict"
        ),
        category=DeprecationWarning,
    )
    if not all(isinstance(k, str) for k in d.keys()):
        raise TypeError("Subtasks must be str")
    if not all(isinstance(v, str) for v in d.values() if v is not None):
        raise TypeError("Subtask log messages must be str or NoneType")

    return OrderedDict(**d)


def run_subtasks(
    cnxn: psycopg2.extensions.connection, subtasks: Dict[pathlib.Path, str]
) -> None:
    """Fetch SQL files and run them in order.

    Args:
        cnxn (psycopg2.extensions.connection): Database connection used to run
            subtasks.
        subtasks (OrderedDict[pathlib.Path, str]): OrderedDict containing paths
            to sql files mapped to the text read by logger.

    Returns:
        None
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.run_subtasks is deprecated; "
            "use alyeska.sqlagent.run_queries_sequentially"
        ),
        category=DeprecationWarning,
    )

    if not all(pathlib.Path(k).suffix == ".sql" for k in subtasks.keys()):
        raise ValueError("Some subtasks are not sql files")
    for subtask, log_text in subtasks.items():
        p = pathlib.Path(subtask)
        logging.info(log_text)
        execute_sql(cnxn, p.read_text())


def run_sql(cnxn: psycopg2.extensions.connection, fp: pathlib.Path, msg: str) -> None:
    """Run SQL: Read from file and execute with connection.

    Args:
        cnxn (psycopg2.extensions.connection): Connection used to execute the SQL
        fp (pathlib.Path): Filepath where target SQL is stored (relative or absolute)
        msg (str): Message for logger when running subtask

    Returns:
        None
    """
    warnings.warn(
        message=(
            "alyeska.sqlagent.run_sql is deprecated; "
            "load the sql into memory as a string and "
            "use alyeska.sqlagent.execute_sql"
        ),
        category=DeprecationWarning,
    )

    if not isinstance(cnxn, psycopg2.extensions.connection):
        raise TypeError("cnxn must be a psycopg2 connection")
    if not isinstance(msg, str):
        raise TypeError("msg must be a str")
    p = pathlib.Path(fp)  # catch error if not a valid path
    if p.suffix == ".sql":
        raise ValueError("fp must be a sql file")

    logging.info(msg)
    query = p.read_text()
    execute_sql(cnxn, query)
