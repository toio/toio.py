#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_cube_off.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pprint
from logging import getLogger

import pytest

from toio.scanner import BLEScanner


logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_cube_off(confirm):
    logger.info("***** TESTS REQUIRED TWO CUBES FINISHED *****")
    logger.info("** turn on only one cube and turn off the rest")


@pytest.mark.asyncio
async def test_confirm_cube_off():
    logger.info("** CHECK THE NUMBER OF CUBES TURNED ON")
    dev = await BLEScanner.scan(2)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 1


