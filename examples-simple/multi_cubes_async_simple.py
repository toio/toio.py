#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     multi_cubes_async_simple.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from logging import DEBUG, INFO

from toio.simple.async_simple import AsyncSimpleCube


async def cube_1():
    print("** ACTIVATE 1")
    async with AsyncSimpleCube(log_level=INFO) as cube:
        print("cube_1:", await cube.get_cube_name())
        await cube.turn_on_cube_lamp(0, 255, 255, 0)
        while not await cube.is_button_pressed():
            await cube.sleep(0)
        print("cube_1: button pressed")
    print("** DISCONNECTED 1")


async def cube_2():
    print("** ACTIVATE 2")
    async with AsyncSimpleCube(log_level=INFO) as cube:
        print("cube_2:", await cube.get_cube_name())
        await cube.turn_on_cube_lamp(255, 255, 0, 0)
        while not await cube.is_button_pressed():
            await cube.sleep(0)
        print("cube_2: button pressed")
    print("** DISCONNECTED 2")


async def main():
    tasks = [cube_1(), cube_2()]
    await asyncio.gather(*tasks)
    print("** END")


if __name__ == "__main__":
    asyncio.run(main())
