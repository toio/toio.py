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
import logging
import sys

from toio.cube.api.indicator import Color, IndicatorParam
from toio.cube.multi_cubes import MultipleToioCoreCubes

logger = logging.getLogger(__name__)


async def scan_and_connect():
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        logger.info("connected")
        await cubes.taro.api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0xFF, g=0x00, b=0xFF))
        )
        await cubes.jiro.api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0xFF))
        )
        await asyncio.sleep(3)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(scan_and_connect()))
