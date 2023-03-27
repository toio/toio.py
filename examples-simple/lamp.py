#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     lamp.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys

from toio.simple import SimpleCube

LOOP = True


def test():
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        print("** CUBE NAME:", cube.get_cube_name())

        print("** WHITE")
        cube.turn_on_cube_lamp(r=255, g=255, b=255, duration=2)
        print("** RED")
        cube.turn_on_cube_lamp(r=255, g=0, b=0, duration=2)
        print("** GREEN")
        cube.turn_on_cube_lamp(r=0, g=255, b=0, duration=2)
        print("** BLUE")
        cube.turn_on_cube_lamp(r=0, g=0, b=255, duration=2)
        print("** OFF")
        cube.turn_off_cube_lamp()

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
