"""Tests for the ci_locksmith.redshift module.

Tests will fail if you don't have valid AWS credentials exported to your dev
environment.
"""

from datetime import datetime
import os

import boto3
import psycopg2
import pytest

import alyeska.locksmith as ls
import alyeska.locksmith.redshift as rs

from test_locksmith_globals import PYTHON_JOB1_SECRET_NAME


def test__parse_jdbc():
    jdbc = """
    jdbc:redshift://myhost:myport/mydb
    """.strip()

    host, port, dbname = rs.parse_jdbc(jdbc)
    assert host == "myhost"
    assert port == "myport"
    assert dbname == "mydb"


def test__parse_secret():
    # mfa = ls.mfa_from_str(CITESTUSER_DEV_CREDENTIALS_STR)
    session = boto3.Session()
    secret = ls.get_secret(
        secret_name=PYTHON_JOB1_SECRET_NAME, session=session, region_name="us-east-1"
    )
    creds = ls.redshift.parse_secret(secret)

    assert isinstance(creds, dict)


def test__connect_with_creds():
    # mfa = ls.mfa_from_str(CITESTUSER_DEV_CREDENTIALS_STR)
    session = boto3.Session()
    secret = ls.get_secret(
        session=session, secret_name=PYTHON_JOB1_SECRET_NAME, region_name="us-east-1"
    )
    creds = ls.redshift.parse_secret(secret)
    cnxn = ls.redshift.connect_with_credentials(**creds)

    assert isinstance(cnxn, psycopg2.extensions.connection)


def test__connect_with_session():
    # mfa = ls.mfa_from_str(CITESTUSER_DEV_CREDENTIALS_STR)
    session = boto3.Session()
    cnxn = rs.connect_with_session(
        session, secret_name=PYTHON_JOB1_SECRET_NAME, region_name="us-east-1"
    )

    assert isinstance(cnxn, psycopg2.extensions.connection)


def test__connect_with_environment():
    cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME)
    assert isinstance(cnxn, psycopg2.extensions.connection)

    cnxn = rs.connect_with_environment(PYTHON_JOB1_SECRET_NAME, enable_autocommit=False)
    assert isinstance(cnxn, psycopg2.extensions.connection)
