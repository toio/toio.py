#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_indicator.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from logging import getLogger

import pytest

from toio.cube import Color, IndicatorParam, ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_indicator_turn_on(indicator, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("** LED ON #FF0080 (purple) 2[s]")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=2000, color=Color(r=0xFF, g=0x00, b=0x80))
    )
    await asyncio.sleep(2)
    logger.info("** LED OFF")
    await asyncio.sleep(2)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_indicator_turn_off_all(indicator, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("** LED ON #00FF40 (light green)")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0x40))
    )
    await asyncio.sleep(3)
    logger.info("** LED OFF")
    await cube.api.indicator.turn_off_all()
    await asyncio.sleep(2)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_indicator_turn_off(indicator, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("** LED ON #00FF40 (light green)")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0x40))
    )
    await asyncio.sleep(3)
    logger.info("** LED OFF")
    await cube.api.indicator.turn_off(1)
    await asyncio.sleep(2)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_indicator_repeated_turn_on(indicator, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("** LED ON #00FF40 (light green) <-> #FF0080 (purple)")
    await cube.api.indicator.repeated_turn_on(
        repeat=5,
        param_list=(
            IndicatorParam(duration_ms=500, color=Color(r=0x00, g=0xFF, b=0x40)),
            IndicatorParam(duration_ms=500, color=Color(r=0xFF, g=0x00, b=0x80)),
        ),
    )
    await asyncio.sleep(5)
    logger.info("** LED OFF")
    await asyncio.sleep(2)
    await cube.api.indicator.turn_off(1)
    await asyncio.sleep(2)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
