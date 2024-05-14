#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     async_gather_multi.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio

from toio.cube.api.button import ButtonState
from toio.cube.multi_cubes import MultipleToioCoreCubes


async def cube1():
    print("cube group 1 connecting...")
    async with MultipleToioCoreCubes(2) as cubes:
        print("cube1-0", cubes[0].name)
        print("cube1-1", cubes[1].name)
        await cubes[0].api.indicator.turn_on((0, 0xFF, 0xFF, 0x00))
        await cubes[1].api.indicator.turn_on((0, 0x10, 0x10, 0x00))
        button = None
        while button is None or button.state == ButtonState.RELEASED:
            button = await cubes[0].api.button.read()
            await asyncio.sleep(0.1)
        print("cube group 1 disconnecting")
    print("cube group 1 disconnected")


async def cube2():
    print("cube group 2 connecting...")
    async with MultipleToioCoreCubes(2) as cubes:
        print("cube2-0", cubes[0].name)
        print("cube2-1", cubes[1].name)
        await cubes[0].api.indicator.turn_on((0, 0x00, 0xFF, 0xFF))
        await cubes[1].api.indicator.turn_on((0, 0x00, 0x10, 0x10))
        button = None
        while button is None or button.state == ButtonState.RELEASED:
            button = await cubes[0].api.button.read()
            await asyncio.sleep(0.1)
        print("cube group 2 disconnecting")
    print("cube group 2 disconnected")


async def main():
    tasks = [cube1(), cube2()]
    await asyncio.gather(*tasks)


asyncio.run(main())
