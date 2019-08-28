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
"""alyeska.logging submodule for configuring basic logs.
"""

import functools
import logging
import time


def config_logging(**kwargs):
    """Default logger configuration

    e.g. 2019-08-13 12:01:14.334 UTC | INFO     | This is a message
    """
    if "format" in kwargs.keys():
        raise ValueError("format is already defined by the default configuration")
    if "level" in kwargs.keys():
        raise ValueError("level is already defined by the default configuration")
    if "datefmt" in kwargs.keys():
        raise ValueError("datefmt is already defined by the default configuration")

    logging.basicConfig(
        format=("%(asctime)s.%(msecs)03d UTC | %(levelname)-8s | %(message)s"),
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        **kwargs,
    )
    logging.Formatter.converter = time.gmtime


def log_scope_change(func):
    """Log when programs enter and exit the decorated function
    """
    # Helps us log the main file being executed.
    # https://stackoverflow.com/a/13240524
    import __main__ as magic_main

    @functools.wraps(func)
    def call(*args, **kwargs):
        """Actual wrapping
        """
        config_logging()
        logging.info(
            f"Entering function '{func.__name__}' in program {magic_main.__file__}"
        )
        result = func(*args, **kwargs)
        logging.info(
            f"Exiting function '{func.__name__}' in program {magic_main.__file__}"
        )
        return result

    return call


@log_scope_change
def sample():
    logging.info("This function is running as expected")
    time.sleep(0.5)
    logging.warning("I have a bad feeling about this.")
    time.sleep(0.5)
    logging.error("Abort! Abort! The eggs are hatching!")
    time.sleep(0.5)
    logging.critical("OH GOD NO IT'S EATING MY FACE")


if __name__ == "__main__":
    sample()
