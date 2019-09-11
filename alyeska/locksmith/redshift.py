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
"""Create AWS Redshift connections

There's a general process to getting connections from Redshift.

1. Authorize the user with MFA; only an authenticated user can access
    secretsmanager. This functionality is in locksmith.
2. Retrieve the secret from secretsmanager using the authorized user.
3. Parse the database credentials from the retrieved secret.
4. Connect to the database with the parsed credentials.

This process can be repeated for other databases, but locksmith.redshift
focuses solely on Redshift connections.
"""

import re

import boto3
import psycopg2

from alyeska.locksmith import get_secret


def parse_jdbc(jdbc: str) -> tuple:
    """Parse the jdbc used for redshift connections

    Args:
        jdbc (str): jdbc connection as str

    Returns:
        tuple: Tuple of host server, port id, and database name
    """
    if not isinstance(jdbc, str):
        raise TypeError("jdbc must be a str")
    m = re.match("jdbc:redshift://(.*?):(.*?)/(.*$)", jdbc)
    host, port, dbname = m.groups()

    return host, port, dbname


def parse_secret(secret: dict) -> dict:
    """Parse credentials from redshift secret. Resulting dict contains

    Args:
        secret (dict): secret as dict with keys "jdbc_connect", "username",
            "wordpass"

    Returns:
        dict: with keys dbname, host, password, port, user
    """
    if not isinstance(secret, dict):
        raise TypeError("secret must be a dict")
    host, port, dbname = parse_jdbc(secret["jdbc_connect"])
    user = secret["username"]
    password = secret["wordpass"]
    creds = {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }

    return creds


def connect_with_credentials(
    host: str, dbname: str, port: str, user: str, password: str
) -> psycopg2.extensions.connection:
    """Setup a psycopg2 connection with a Redshift database using supplied
    credentials.

    Note that `server` must be a web address. You'll need to remove prefixes
    like 'jdbc:sqlserver://'. Similarly, suffixes specifying the port and/or
    database must also be removed.

    Args:
        host (str): Host server URI
        dbname (str): database name
        port (str): Port ID
        user (str): Username
        password (str): User password

    Returns:
        psycopg2.extensions.connection: Redshift connection
    """
    if not isinstance(host, str):
        raise TypeError("`host` must be a str.")
    if not isinstance(dbname, str):
        raise TypeError("`dbname` must be a str.")
    if not isinstance(port, str):
        raise TypeError("`port` must be a str.")
    if not isinstance(user, str):
        raise TypeError("`user` must be a str.")
    if not isinstance(password, str):
        raise TypeError("`password` must be a str.")

    cnxn = psycopg2.connect(
        f"""
        host={host}
        dbname={dbname}
        port={port}
        user={user}
        password={password}
        """
    )

    return cnxn


def connect_with_session(
    session: boto3.Session,
    secret_name: str,
    *,
    enable_autocommit: bool = True,
    region_name: str = "us-east-1",
) -> psycopg2.extensions.connection:
    """Use the AWS MFA credentials in your session to retrieve secret from
    secretsmanager, parse credentials from the secret, and use the parsed
    credentials to connect to redshift.


    Args:
        session (boto3.Session): session used to query AWS secretsmanager
        secret_name (str): secret name recognized by AWS secretsmanager
        enable_autocommit (bool, optional): Whether to enable autocommit on
            the Redshift connection. Defaults to True.
        region_name (str, optional): AWS region. Defaults to "us-east-1".

    Raises:
        ValueError: If AWS secretsmanager doesn't return a secret for the
            supplied secret_name

    Returns:
        psycopg2.extensions.connection: Redshift connection
    """
    if not isinstance(session, boto3.Session):
        raise TypeError("session must be a boto3 Session")
    if not isinstance(secret_name, str):
        raise TypeError("secret_name must be a str")
    if not isinstance(enable_autocommit, bool):
        raise TypeError("enable_autocommit must be a bool")
    if not isinstance(region_name, str):
        raise TypeError("region_name must be a str")

    secret = get_secret(
        session=session, secret_name=secret_name, region_name=region_name
    )
    if secret is None:
        raise ValueError(
            "No secret returned. Is your MFA authorized to access this secret? "
            "Is there a typo in the secret?"
        )
    creds = parse_secret(secret)
    cnxn = connect_with_credentials(**creds)
    cnxn.autocommit = enable_autocommit

    return cnxn


def connect_with_profile(
    profile_name: str, secret_name: str, **kwargs
) -> psycopg2.extensions.connection:
    """Creates a session from the local profile name and returns
    connect_with_session(profile_name, secret_name).

    View your .aws/credentials file to identify valid profiles.

    Args:
        secret_name (str): secret name recognized by AWS secretsmanager
        profile_name (str, optional): AWS profile name. Defaults to None.
        **kwargs are same as connect_with_session

    Returns:
        psycopg2.extensions.connection: Connection to Redshift database
    """
    if not isinstance(profile_name, str):
        raise TypeError(
            "profile_name must be a str "
            "or None if connecting with environment variables"
        )

    session = boto3.Session(profile_name=profile_name)
    cnxn = connect_with_session(session, secret_name, **kwargs)

    return cnxn


def connect_with_environment(
    secret_name: str, **kwargs
) -> psycopg2.extensions.connection:
    """Creates a session from the local environment variables and returns
    connect_with_session(profile_name, secret_name).

    If connecting through an MFA user, your environment variables must be:
        AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY
        AWS_SESSION_TOKEN

    Args:
        secret_name (str): secret name recognized by AWS secretsmanager
        **kwargs are same as connect_with_session

    Returns:
        psycopg2.extensions.connection: Connection to Redshift database
    """
    session = boto3.Session()
    cnxn = connect_with_session(session, secret_name, **kwargs)

    return cnxn
