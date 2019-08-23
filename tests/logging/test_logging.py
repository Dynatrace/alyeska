import logging

import pytest

from alyeska.logging import config_logging


def test__config_logging(caplog):
    config_logging()
    logging.info("Test message")
    print(caplog.text)


if __name__ == "__main__":
    config_logging()
