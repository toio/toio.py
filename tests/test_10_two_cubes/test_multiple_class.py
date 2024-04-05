#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     multi.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from logging import getLogger

import pytest

from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube
from toio.cube.multi_cubes import MultipleToioCoreCubes
from toio.cube.api.indicator import IndicatorParam, Color
from toio.scanner import BLEScanner

logger = getLogger(__name__)

@pytest.mark.asyncio
async def test_multiple_1():
    logger.info("** CONNECTING...")
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        logger.info("** CONNECTED")
        assert len(cubes) == 2

        await cubes.taro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0xff, g=0x00, b=0xff)))
        await cubes.jiro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xff, b=0xff)))
        await asyncio.sleep(3)
        logger.info("** DISCONNECTING")
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_multiple_2():
    logger.info("** SCANTING...")
    cube_list = await BLEScanner.scan(num=2)
    logger.info("** SCAN COMPLETE")
    assert len(cube_list) == 2

    cube_name = ("taro", "jiro")

    logger.info("** CONNECTING...")
    cubes = MultipleToioCoreCubes(cube_list, cube_name)
    assert len(cubes) == 2
    await cubes.connect()
    logger.info("** CONNECTED")

    taro: ToioCoreCube = cubes.named("taro")
    jiro: ToioCoreCube = cubes.named("jiro")

    await taro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0xff, g=0x00, b=0xff)))
    await jiro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xff, b=0xff)))

    await asyncio.sleep(3)
    logger.info("** DISCONNECTING")
    await cubes.disconnect()
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_multiple_3():
    logger.info("** CONNECTING...")
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        logger.info("** CONNECTED")
        assert len(cubes) == 2

        for c in cubes:
            await c.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0xff, g=0x00, b=0xff)))
            await asyncio.sleep(2)
            await c.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0x00, b=0x00)))
        logger.info("** DISCONNECTING")
    logger.info("** DISCONNECTED")

