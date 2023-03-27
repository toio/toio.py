#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     basic_motor_control.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys
from logging import INFO

from toio.simple import SimpleCube


def test():
    print("** ACTIVATE")
    # with SimpleCube(name="31j", debug=False) as cube:
    # with SimpleCube(name="h7p", debug=False) as cube:
    with SimpleCube(
        log_level=INFO
    ) as cube:  # try to connect to registered, otherwise connect to nearest
        print("** CONNECTED")
        print("** MOVE")
        cube.move(30, 3)
        print("** SPIN")
        cube.spin(60, 2)
        print("** RUN MOTOR")
        cube.run_motor(70, 10, 1)
        cube.run_motor(10, 70, 1)
        cube.run_motor(-20, -20, 0)
        print("** STOP MOTOR")
        cube.sleep(0.5)
        cube.stop_motor()
    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
