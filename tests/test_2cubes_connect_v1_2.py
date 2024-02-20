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
    cube = ToioCoreCube.create(device_list)
    assert isinstance(cube, ToioCoreCube)
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
    device_list = await BLEScanner.scan(2)
    assert len(device_list)
    cubes = ToioCoreCube.create_cubes(device_list)
    assert isinstance(cubes, list)
    logger.info("** CONNECTING...")
    for cube in cubes:
        await cube.connect()
    logger.info("** CONNECTED")
    for n in range(50):
        logger.info("--")
        for i in range(len(cubes)):
            pos = await cubes[i].api.id_information.read()
            xx = str(pos)
            logger.info("cube[%d]: %4d:%s",i , n, xx)
    logger.info("** DISCONNECTING")
    for cube in cubes:
        await cube.disconnect()
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_connect_3():
    with pytest.raises(ValueError) as ex:
        cube = ToioCoreCube.create([1, 2, 3])
    logger.info(ex)

@pytest.mark.asyncio
async def test_connect_4():
    with pytest.raises(ValueError) as ex:
        cube = ToioCoreCube.create(1)
    logger.info(ex)

@pytest.mark.asyncio
async def test_connect_5():
    with pytest.raises(ValueError) as ex:
        cube = ToioCoreCube.create([])
    logger.info(ex)

