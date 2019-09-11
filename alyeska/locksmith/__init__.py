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
"""Fetch credentials from AWS Secrets Manager.

Usage:
    >>> import boto3
    >>> import alyeska.locksmith as ls
    >>> session = boto3.Session()  # fetch creds from .aws/credentials
    >>> secret_name = "my-super-secret-secret"
    >>> secret = ls.get_secret(session, secret_name)
"""

from datetime import datetime
import json
import logging
import os
from typing import Tuple

import boto3
from botocore.exceptions import ClientError


def mfa_from_str(json_str: str, *, include_expiration=False) -> dict:
    """Create credentials dict from credentials as a json string.

    This function is a thin wrapper around json.loads

    Args:
        json_str (str): String containing a json object. e.g.
            '''
            {
                "Credentials": {
                    "AccessKeyId": "FAKEACCESSKEY",
                    "SecretAccessKey": "Fake+Secret9Access-Key",
                    "SessionToken": "f4k3-SE5510N_t0k3n",
                    "Expiration": "2019-07-30T00:14:27Z"
                }
            }
            '''
        include_expiration (bool, optional): Whether to include expiration in
            returned json. Defaults to False.

    Returns:
        dict: with types as
            {
                "aws_access_key_id": str,
                "aws_secret_access_key": str,
                "aws_session_token": str,
                "expiration": datetime,
            }

    Example:
        >>> import dynatrace_locksmith as ls
        >>> creds = ls.mfa_from_str(json_str)
        >>> creds
        {
            "Credentials": {
                "AccessKeyId": "1234567890",
                "SecretAccessKey": "qwertyuiop",
                "SessionToken": "asdfghjklzxcvbnm",
                "Expiration": "2018-11-02T05:15:21Z"
            }
        }

        >>> session = boto3.Session(**creds)
    """
    if not isinstance(json_str, str):
        raise TypeError("json_str must be a str")
    if not isinstance(include_expiration, bool):
        raise TypeError("include_expiration must be a bool")

    creds = json.loads(json_str)["Credentials"]
    creds["aws_access_key_id"] = creds.pop("AccessKeyId")
    creds["aws_secret_access_key"] = creds.pop("SecretAccessKey")
    creds["aws_session_token"] = creds.pop("SessionToken")

    expiration = creds.pop("Expiration")
    if include_expiration:
        creds["expiration"] = datetime.strptime(
            expiration.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z"
        )

    return creds


def get_secret(
    session: boto3.Session, secret_name: str, region_name: str = "us-east-1"
) -> dict:
    """Get secret from secretsmanager using an established session.

    See boto3.amazonaws.com/v1/documentation/api/latest/guide/secrets-manager.html

    Args:
        session (boto3.Session): [description]
        secret_name (str): [description]
        region_name (str, optional): [description]. Defaults to "us-east-1".

    Returns:
        dict: Secret as dict
    """
    if not isinstance(session, boto3.Session):
        raise TypeError("session must be a boto3.Session")
    if not isinstance(secret_name, str):
        raise TypeError("secret_name must be a str")
    if not isinstance(region_name, str):
        raise TypeError("region_name must be a str")

    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logging.error(f"The requested secret {secret_name} was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logging.error(f"The request was invalid: {e}")
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logging.error(f"The request had invalid params: {e}")
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            logging.error(f"The request for secret {secret_name} was denied")
        else:
            raise (e)
    else:
        # Secrets Manager decrypts the secret value using the associated
        # KMS CMK. Depending on whether the secret was a string or binary,
        # only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            text_secret_data = get_secret_value_response["SecretString"]
            return json.loads(text_secret_data)
        else:
            raise TypeError("SecretString not found. Byte responses not supported.")
