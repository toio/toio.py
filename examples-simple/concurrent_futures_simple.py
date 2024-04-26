#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     async_gather_simple.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

from concurrent import futures
from logging import INFO

from toio.simple import SimpleCube


def cube1():
    with SimpleCube(log_level=INFO) as cube:
        print("taro", cube.get_cube_name())
        cube.turn_on_cube_lamp(0xFF, 0xFF, 0x00, 0)
        while not cube.is_button_pressed():
            cube.sleep(0.1)
        print("taro disconnecting")
    print("taro disconnected")


def cube2():
    with SimpleCube(log_level=INFO) as cube:
        print("jiro", cube.get_cube_name())
        cube.turn_on_cube_lamp(0x00, 0xFF, 0xFF, 0)
        while not cube.is_button_pressed():
            cube.sleep(0.1)
        print("jiro disconnecting")
    print("jiro disconnected")


def main():
    with futures.ThreadPoolExecutor() as executor:
        executor.submit(cube1)
        executor.submit(cube2)


main()
