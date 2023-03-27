#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     angle_control.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys

from toio.simple import SimpleCube


def test():
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        print("** ZERO")
        cube.set_orientation(30, 0)
        cube.sleep(2)

        print("** SET DIRECTION (POSITIVE ANGLE)")
        cube.set_orientation(30, 0)
        cube.sleep(0.7)
        cube.set_orientation(30, 45)
        cube.sleep(0.7)
        cube.set_orientation(30, 90)
        cube.sleep(0.7)
        cube.set_orientation(30, 180)
        cube.sleep(0.7)
        cube.set_orientation(30, 270)
        cube.sleep(0.7)
        cube.set_orientation(30, 360)
        cube.sleep(0.7)
        print("** SET DIRECTION (NEGATIVE ANGLE)")
        cube.set_orientation(30, -315)
        cube.sleep(0.7)
        cube.set_orientation(30, -270)
        cube.sleep(0.7)
        cube.set_orientation(30, -180)
        cube.sleep(0.7)
        cube.set_orientation(30, -90)
        cube.sleep(0.7)
        cube.set_orientation(30, -1)
        cube.sleep(0.7)

        print("** TURN (POSITIVE ANGLE)")
        for _ in range(8):
            cube.turn(30, 45)
            cube.sleep(0.7)
        print("** TURN (NEGATIVE ANGLE)")
        for _ in range(8):
            cube.turn(30, -45)
            cube.sleep(0.7)
        print("** SET ORIENTATION 90")
        cube.set_orientation(30, 90)
        print("** STOP MOTOR")
        cube.sleep(0.5)
        cube.stop_motor()
    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
