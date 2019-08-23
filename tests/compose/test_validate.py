import pytest

from alyeska.compose.exceptions import ConfigurationError
from alyeska.compose.validate import validate_config

from test_compose_globals import (
    COMPOSE_SMALL,
    COMPOSE_BIG,
    COMPOSE_CYCLE,
    COMPOSE_TRICKY,
)

VALID_CONFIG = {
    "version": "2019.8.15",
    "conda-envs": {
        "base": "base",
        "ci-python36-2.1": "ci-python36-2.1",
        "python36-2019.8.14": "python36-2019.8.14",
    },
    "tasks": {
        "hello": {"loc": "/path/to/hello", "env": "base"},
        "world": {"loc": "/path/to/world", "env": "base", "uses": "hello"},
    },
}


def test__validate_config():

    with pytest.raises(ConfigurationError):
        validate_config(dict())

    with pytest.raises(ConfigurationError):
        invalid_config = VALID_CONFIG.copy()
        invalid_config.pop("version")
        validate_config(invalid_config)

    with pytest.raises(ConfigurationError):
        invalid_config = VALID_CONFIG.copy()
        invalid_config.pop("conda-envs")
        validate_config(invalid_config)

    with pytest.raises(ConfigurationError):
        invalid_config = VALID_CONFIG.copy()
        invalid_config.pop("tasks")
        validate_config(invalid_config)

    with pytest.raises(ConfigurationError):
        invalid_config = VALID_CONFIG.copy()
        invalid_config["unrecognized-key"] = 1234
        validate_config(invalid_config)

    # valid example
    validate_config(VALID_CONFIG)


# def test__validate_version():
#     with pytest.raises(ConfigurationError):
#         invalid_config = VALID_CONFIG.copy()
#         invalid_config["version"] = "0"
#         validate_config(invalid_config)
