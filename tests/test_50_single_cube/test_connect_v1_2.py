#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_connect_v1_2.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
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
    assert not cube.is_connect()
    await cube.connect()
    assert cube.is_connect()
    logger.info("** CONNECTED")
    for n in range(100):
        pos = await cube.api.id_information.read()
        xx = str(pos)
        logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECT")
    await cube.disconnect()
    assert not cube.is_connect()


@pytest.mark.asyncio
async def test_connect_2():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    async with ToioCoreCube(device_list[0].interface) as cube:
        assert cube.is_connect()
        logger.info("** CONNECTED")
        for n in range(100):
            pos = await cube.api.id_information.read()
            xx = str(pos)
            logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECTED")
    assert not cube.is_connect()


@pytest.mark.asyncio
async def test_connect_3():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    assert not cube.is_connect()
    await cube.connect()
    assert cube.is_connect()
    logger.info("** CONNECTED")
    logger.info("** RE-CONNECTING...")
    await cube.connect()
    assert cube.is_connect()
    for n in range(10):
        pos = await cube.api.id_information.read()
        xx = str(pos)
        logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECT")
    await cube.disconnect()
    assert not cube.is_connect()
    logger.info("** RE-DISCONNECT")
    await cube.disconnect()
    assert not cube.is_connect()


@pytest.mark.asyncio
async def test_connect_4():
    async with ToioCoreCube() as cube:
        assert cube.is_connect()
        logger.info("** CONNECTED: %s", cube.name)
        for n in range(100):
            pos = await cube.api.id_information.read()
            xx = str(pos)
            logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECTED")
    assert not cube.is_connect()


@pytest.mark.asyncio
async def test_connect_5():
    async with ToioCoreCube(name="taro") as cube:
        assert cube.is_connect()
        assert cube.name == "taro"
        logger.info("** CONNECTED: %s", cube.name)
        for n in range(100):
            pos = await cube.api.id_information.read()
            xx = str(pos)
            logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECTED")
    assert not cube.is_connect()


@pytest.mark.asyncio
async def test_connect_6():
    async with ToioCoreCube(name="taro") as cube:
        assert cube.is_connect()
        assert cube.name == "taro"
        logger.info("** CONNECTED: %s", cube.name)
        for n in range(100):
            pos = await cube.api.id_information.read()
            xx = str(pos)
            logger.info("%4d:%s", n, xx)
    logger.info("** DISCONNECTED")
    assert not cube.is_connect()
