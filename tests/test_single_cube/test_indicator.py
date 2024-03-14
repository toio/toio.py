#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_connect.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio

import pytest

from toio.cube import Color, IndicatorParam, ToioCoreCube
from toio.scanner import BLEScanner


@pytest.mark.asyncio
async def test_indicator_turn_on():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    print("** CONNECTING...")
    await cube.connect()
    print("** CONNECTED")
    print("** LED ON #FF0040 (2[s])")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=2000, color=Color(r=0xFF, g=0x00, b=0x40))
    )
    await asyncio.sleep(5)
    print("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_indicator_turn_off_all():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    print("** CONNECTING...")
    await cube.connect()
    print("** CONNECTED")
    print("** LED ON #00FF40")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0x40))
    )
    await asyncio.sleep(3)
    print("** LED OFF")
    await cube.api.indicator.turn_off_all()
    await asyncio.sleep(2)
    print("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_indicator_turn_off():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    print("** CONNECTING...")
    await cube.connect()
    print("** CONNECTED")
    print("** LED ON #00FF40")
    await cube.api.indicator.turn_on(
        IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0x40))
    )
    await asyncio.sleep(3)
    print("** LED OFF")
    await cube.api.indicator.turn_off(1)
    await asyncio.sleep(2)
    print("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_indicator_repeated_turn_on():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    print("** CONNECTING...")
    await cube.connect()
    print("** CONNECTED")
    print("** LED ON #00FF40 <-> #FF0040")
    await cube.api.indicator.repeated_turn_on(
        repeat=5,
        param_list=(
            IndicatorParam(duration_ms=500, color=Color(r=0x00, g=0xFF, b=0x40)),
            IndicatorParam(duration_ms=500, color=Color(r=0xFF, g=0x00, b=0x40)),
        ),
    )
    await asyncio.sleep(13)
    print("** LED OFF")
    await cube.api.indicator.turn_off(1)
    await asyncio.sleep(2)
    print("** DISCONNECT")
    await cube.disconnect()
