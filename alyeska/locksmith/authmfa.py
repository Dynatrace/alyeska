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
"""Fetch MFA credentials to access AWS remotely

Export the variables to the local script in one line using:
    $ eval `authmfa ProfileName`

http://blog.tintoy.io/2017/06/exporting-environment-variables-from-python-to-bash/
"""
import argparse
from configparser import ConfigParser
from json import dump as json_dump
import os
import pathlib
from typing import Dict, Tuple

import boto3
import pyotp


def parse_aws_credentials(profile_name: str) -> Tuple[str, str, str, str]:
    """Find .aws/credentials file and collect AWS credentials under the
    given profile

    Args:
        profile_name (str): Which profile's credentials to fetch

    Returns:
        Tuple[str, str, str, str]: A tuple of user_name, account_name,
            aws_account_id, and aws_mfa_seed
    """
    config = ConfigParser()
    config.read([os.path.join(os.path.expanduser("~"), ".aws", "credentials")])

    user_name = config.get(profile_name, "user_name")
    account_name = config.get(profile_name, "account_name")
    account_id = config.get(profile_name, "aws_account_id")
    mfa_seed = config.get(profile_name, "aws_mfa_seed")

    return user_name, account_name, account_id, mfa_seed


def get_totp(seed: str) -> str:
    """Calculate the TOTP secret from the given seed

    Args:
        seed (str): The seed to the TOTP secret

    Returns:
        str: a 6-digit numeric string
    """
    totp = pyotp.TOTP(seed)
    token_code = totp.now()

    return token_code


def get_session_token(
    profile_name: str, user_name: str, account_id: str, token_code: str
) -> str:
    """Fetch temporary creds from AWS

    Args:
        profile_name (str):
        user_name (str):
        account_id (str):
        token_code (str):

    Returns:
        str: A json string with credentials and such
    """
    session = boto3.Session(profile_name=profile_name)
    client = session.client("sts")
    kw = {
        "SerialNumber": f"arn:aws:iam::{account_id}:mfa/{user_name}",
        "TokenCode": f"{token_code}",
        "DurationSeconds": 60 * 60 * 12,
    }
    response = client.get_session_token(**kw)
    return response


def to_file(response: Dict, fp: pathlib.Path = "aws_creds.json") -> None:
    """Write response to file

    Args:
        response (Dict): Response from get_session_token
        fp (pathlib.Path, optional): Where to store the response. Defaults to
            "aws_creds.json".

    Returns:
        None
    """
    response_dict = dict(response)
    p = pathlib.Path(fp)
    with p.open("w") as ofile:
        json_dump(response_dict, ofile, indent=4, sort_keys=True, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch MFA credentials for the given AWS profile",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "profile_name",
        metavar="profile_name",
        type=str,
        help=(
            "profile name from .aws/credentials. Credentials should contain a "
            "user_name, account_name, aws_account_id, and aws_mfa_seed in your "
            ".aws/credentials file. e.g.\n"
            "[ProfileName]\n"
            "region = us-east-1\n"
            "aws_access_key_id = ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "aws_secret_access_key = nOt/A-Re4l_sEcReT-kEy\n"
            "# start help authmfa ---------------\n"
            "user_name = Profile\n"
            "account_name = dev\n"
            "aws_account_id = 1234567890\n"
            "aws_mfa_seed = whatever-your-seed-is\n"
            "# end help authmfa -----------------"
        ),
    )
    args = parser.parse_args()

    user_name, _, account_id, mfa_seed = parse_aws_credentials(args.profile_name)
    token_code = get_totp(mfa_seed)
    response = get_session_token(args.profile_name, user_name, account_id, token_code)

    creds = response["Credentials"]
    AWS_ACCESS_KEY_ID = creds["AccessKeyId"]
    AWS_SECRET_ACCESS_KEY = creds["SecretAccessKey"]
    AWS_SESSION_TOKEN = creds["SessionToken"]

    print(f"export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}")
    print(f"export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}")
    print(f"export AWS_SESSION_TOKEN={AWS_SESSION_TOKEN}")
