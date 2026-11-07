#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_cube_off.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
from logging import getLogger

import pytest

from toio.cube import ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_cube_off():
    logger.info("***** TEST AUTOMATED REMOTE POWER OFF *****")
    logger.info("** CHECK THE NUMBER OF CUBES TURNED ON")
    dev = await BLEScanner.scan(2)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 2

    # Connect to one of the cubes and turn it off after 2 seconds
    cube = ToioCoreCube(dev[0].interface)
    await cube.connect()
    logger.info("** WAIT 2 SECONDS AFTER CONNECTION")
    await asyncio.sleep(2)
    logger.info("** REQUEST REMOTE POWER OFF AFTER 2 SECONDS")
    await cube.api.configuration.request_remote_power_off(2)
    await cube.disconnect()

    # Wait for the cube to turn off (2s + buffer)
    logger.info("** WAITING FOR 5 SECONDS...")
    await asyncio.sleep(5)

    logger.info("** CHECK THE NUMBER OF CUBES TURNED ON AGAIN")
    dev_after = await BLEScanner.scan(2, timeout=5)
    for d in dev_after:
        pprint.pprint(d)
    assert len(dev_after) == 1
