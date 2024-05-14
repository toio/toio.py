#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     async_task_group.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import sys

from toio.cube import ToioCoreCube
from toio.cube.api.button import ButtonState


async def cube1():
    print("cube1 connecting...")
    async with ToioCoreCube() as cube:
        print("cube1", cube.name)
        await cube.api.indicator.turn_on((0, 0xFF, 0xFF, 0x00))
        button = None
        while button is None or button.state == ButtonState.RELEASED:
            button = await cube.api.button.read()
            await asyncio.sleep(0.1)
        print("cube1 disconnecting")
    print("cube1 disconnected")


async def cube2():
    print("cube2 connecting...")
    async with ToioCoreCube() as cube:
        print("cube2", cube.name)
        await cube.api.indicator.turn_on((0, 0x00, 0xFF, 0xFF))
        button = None
        while button is None or button.state == ButtonState.RELEASED:
            button = await cube.api.button.read()
            await asyncio.sleep(0.1)
        print("cube2 disconnecting")
    print("cube2 disconnected")


async def main():
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(cube1())
            tg.create_task(cube2())
    else:
        print("TaskGroup is not supported python %d.%d" % (sys.version_info.major, sys.version_info.minor))
        print("Supported by Python 3.11 or later")


asyncio.run(main())
