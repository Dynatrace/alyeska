Alyeska /al-ee-EHS-kah/ n. A Data Engineering Toolkit
=====================================================

.. image:: https://img.shields.io/pypi/v/alyeska.svg?color=blue
    :alt: Version
    :target: https://pypi.org/project/alyeska/

.. image:: https://img.shields.io/badge/Licence-Apache%202.0-blue.svg
    :alt: License
    :target: ./LICENSE

.. image:: https://img.shields.io/pypi/pyversions/alyeska.svg
    :alt: Supported Versions
    :target: https://pypi.org/project/alyeska/

.. image:: https://img.shields.io/github/last-commit/Dynatrace/alyeska.svg
    :alt: Last Commit
    :target: https://github.com/Dynatrace/alyeska

.. image:: https://img.shields.io/github/issues/Dynatrace/alyeska/bug?color=red
    :alt: Count Bugs
    :target: https://github.com/Dynatrace/alyeska/issues?q=is%3Aopen+is%3Aissue+label%3Abug

.. image:: https://img.shields.io/travis/com/Dynatrace/alyeska/master
    :alt: Build Status
    :target: https://github.com/Dynatrace/alyeska

.. image:: https://readthedocs.org/projects/alyeska/badge/?version=latest
    :alt: Documentation Status
    :target: https://alyeska.readthedocs.io/en/latest/?badge=latest


Alyeska is a data engineering toolkit to simplify the nuts & bolts of data engineering tasks.

More concretely, alyeska bridges the gap between common Python modules and common data engineering technologies. i.e. pandas, psycopg2, AWS Redshift, AWS secretsmanager, and more. Alyeska offers simple functions and/or syntactic sugar to common tasks:

* Safely executing many SQL statements against a database (``sqlagent``)
* Loading a pandas dataframe into a database (``redpandas``)
* Assuming an AWS IAM user with multi-factor authorization (``locksmith.authmfa``)
* Creating psycopg2 connections to Redshift (``locksmith``)
* Generate shell scripts that respect workflow dependencies (``compose.compose_sh``)

While Alyeska mimics some functionalities, it is not a replacement for Airflow, AWS Glue, or other purpose-built data engineering technologies. That is, metaphorically, Alyeska is your parents' toolbox. While terrific for fixing a leaky faucet, but it is no replacement for a plumber.

Sample Usage
------------

**Assume an AWS IAM user with multi-factor authorization**

Alyeska's ``authmfa`` command line utility is useful for quickly assuming an AWS IAM user with MFA.

.. code-block:: sh

    $ authmfa MyAwsUser
    export AWS_ACCESS_KEY_ID=ABCDEFGHIJKLMNOPQRSTUVWXYZ
    export AWS_SECRET_ACCESS_KEY=abcdefg1234567!@#$%^&
    export AWS_SESSION_TOKEN=notarealsessiontoken///////5AVHwuGc*hYLp%$vr51*XTEHJjRD2JxavaD8wlJqi!aCZVhvp7nzt!U5elvoPZ@GlG%a9sT^HBrgKzQ8xZrpAADp65RYQzqvawF
    $ eval `authmfa MyAwsUser`  # export to environment

Learn more about how to config this utility with ``authmfa -h``.

**Load a pandas dataframe into AWS Redshift**

Large tables can be frustrating to load into Redshift. Alyeska reduces the process to a short one-line statement:

.. code-block:: python

    >>> aly.redpandas.insert_pandas_into(cnxn, target_table, payload_df)

In practice, it may function as

.. code-block:: python

    >>> import alyeska as aly
    >>> import alyeska.locksmith.redshift as rs
    >>> import pandas as pd

    >>> cnxn = rs.connect_with_environment("my-user")
    >>> target_table = "db.natural_numbers"

    >>> sql = f"CREATE TABLE {target_table}(n INT NOT NULL)"
    >>> aly.sqlagent.execute_sql(cnxn, sql)  # create table

    >>> natural_numbers_df = pd.DataFrame({"n": range(1, 1_000_001)})
    >>> aly.redpandas.insert_pandas_into(cnxn, target_table, natural_numbers_df)

Components
----------

Tools are broken out into modules with niche purposes:

1. ``compose`` is a workflow dependency management tool
2. ``locksmith`` helps authorize AWS sessions and Redshift connections
3. ``logging`` is another thin module that standardizes logging practices
4. ``redpandas`` supports less verbose pandas/redshift functionality
5. ``sqlagent`` supports SQL executation and runtime configuration

License
-------

This project is licensed under the Apache v2.0 License - see the LICENSE_ file for details.

Contribute
----------

Begin by reading our `Code of Conduct`_.

There are some devtools required to contribute to the repo. Create a development environment and install pre-commit to run hooks on your code.

.. code-block:: sh

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r requirements.dev.txt
    $ pre-commit install
    $ pre-commit autoupdate

Namesake
--------

The Alyeska Pipeline Service company maintains the Alaska pipeline; a 1200 km long pipeline connecting the oil-rich, subterranean earth in Alaska to port on the north pacific ocean.

.. _LICENSE: https://github.com/Dynatrace/alyeska/blob/master/LICENSE
.. _Code of Conduct: https://github.com/Dynatrace/alyeska/blob/master/code-of-conduct.rst
