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
"""Tests for the locksmith submodule.

Tests will fail if you don't have valid AWS credentials exported to your dev
environment.
"""

from datetime import datetime
import os
import pathlib

import boto3
import psycopg2
import pytest

import alyeska.locksmith as ls
import alyeska.locksmith.redshift as rs

ALYESKA_REDSHIFT_SECRET = os.getenv("ALYESKA_REDSHIFT_SECRET")

CITESTUSER_DEV_CREDENTIALS_FP = pathlib.Path(
    os.path.dirname(__file__), "sample-credentials.txt"
)
# File looks like
# {
#     "Credentials": {
#         "AccessKeyId": "FAKEACCESSKEY",
#         "SecretAccessKey": "Fake+Secret9Access-Key",
#         "SessionToken": "y7u893t489yh34tg89awyh4tg9yhqa34p98hQA34&ANJ4IGa3w48iahj34wegha:4RGHN",
#         "Expiration": "2019-07-30T00:14:27Z"
#     }
# }

with CITESTUSER_DEV_CREDENTIALS_FP.open("r") as ifile:
    CITESTUSER_DEV_CREDENTIALS_STR = ifile.read()


def test_mfa_from_str():
    mfa = ls.mfa_from_str(CITESTUSER_DEV_CREDENTIALS_STR, include_expiration=True)
    assert isinstance(mfa["aws_access_key_id"], str)
    assert isinstance(mfa["aws_secret_access_key"], str)
    assert isinstance(mfa["aws_session_token"], str)
    assert isinstance(mfa["expiration"], datetime)


def test__get_secret():
    session = boto3.Session()

    secret = ls.get_secret(
        secret_name=ALYESKA_REDSHIFT_SECRET, session=session, region_name="us-east-1"
    )

    assert isinstance(secret, dict)
