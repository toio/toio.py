#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     step.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys

from toio.simple import Direction, SimpleCube


def step_test():
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        print("** MOVE STEPS")
        cube.move_steps(Direction.Forward, 30, 50)
        cube.move_steps(Direction.Backward, 30, 50)
        print("** END")


if __name__ == "__main__":
    sys.exit(step_test())
