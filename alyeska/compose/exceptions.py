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
"""Exceptions that are unique to the composer module.
"""


class CyclicGraphError(Exception):
    """Composer will generate an infinite schedule given a cyclic graph"""


class EarlyAbortError(Exception):
    """Used in conjunction with Composer.run_tasks() for error handling"""


class ConfigurationError(Exception):
    """For configuration errors with the compose.yaml file"""
