#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     move_to.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys

from toio.simple import SimpleCube


def test():
    targets = ((30, 30), (30, -30), (-30, -30), (-30, 30), (30, 30))
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        for target in targets:
            target_pos_x, target_pos_y = target
            print(f"move to ({target_pos_x}, {target_pos_y})")
            success = cube.move_to(speed=70, x=target_pos_x, y=target_pos_y)
            print(f"arrival: {success}")
            if not success:
                print("Position ID missed")
                break
            cube.sleep(0.5)
    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
