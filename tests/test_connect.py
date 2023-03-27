#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_connect.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from logging import getLogger

import pytest

from toio.cube import ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_connect_1():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    for n in range(100):
        pos = await cube.api.id_information.read()
        xx = str(pos)
        logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_connect_2():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    async with ToioCoreCube(device_list[0].interface) as cube:
        logger.info("** CONNECTED")
        for n in range(100):
            pos = await cube.api.id_information.read()
            xx = str(pos)
            logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_connect_3():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("** RE-CONNECTING...")
    await cube.connect()
    for n in range(10):
        pos = await cube.api.id_information.read()
        xx = str(pos)
        logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECT")
    await cube.disconnect()
    logger.info("** RE-DISCONNECT")
    await cube.disconnect()
