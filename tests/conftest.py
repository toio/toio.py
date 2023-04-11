# -*- coding: utf-8 -*-
# ************************************************************
#
#     conftest.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import time
from logging import getLogger

import pytest

logger = getLogger(__name__)

@pytest.fixture(scope="function", autouse=True)
def wait():
    logger.info("PRE WAIT")
    time.sleep(2)
