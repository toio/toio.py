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
import sys

from toio.cube import ToioCoreCube
from toio.cube.multi_cubes import MultipleToioCoreCubes
from toio.cube.api.indicator import IndicatorParam, Color
from toio.scanner import BLEScanner


import logging

logger = logging.getLogger(__name__)

async def scan_and_connect():
    # print("scan")
    # cube_list = await BLEScanner.scan(num=2)

    # print("complete to scan")
    # assert len(cube_list) == 2
    # cube_name = ("taro", "jiro")

    # cubes = MultiCubes(cube_list, cube_name)
    # await cubes.connect()

    # taro: ToioCoreCube = cubes.named("taro")
    # jiro: ToioCoreCube = cubes.named("jiro")

    # await taro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0xff, g=0x00, b=0xff)))
    # await jiro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xff, b=0xff)))

    # await asyncio.sleep(3)
    # await cubes.disconnect()

    # async with MultipleCubes(cube_list, cube_name) as cubes:
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        logger.info("connected")
        await cubes.taro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0xff, g=0x00, b=0xff)))
        await cubes.jiro.api.indicator.turn_on(IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xff, b=0xff)))
        await asyncio.sleep(3)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(scan_and_connect()))
