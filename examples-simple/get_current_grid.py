#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     get_current_grid.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys

from toio.simple import SimpleCube


def test():
    print("** ACTIVATE")
    cube = SimpleCube()
    previous_grid = None
    print("** CONNECTED")
    try:
        while True:
            current_grid = cube.get_grid()
            if current_grid and current_grid != previous_grid:
                print(current_grid)
            previous_grid = current_grid
            if cube.is_button_pressed():
                break
            cube.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupt")
    finally:
        print("** DISCONNECTING (PLEASE WAIT)")
        cube.disconnect()
        print("** DISCONNECTED")
        print("** END")


if __name__ == "__main__":
    sys.exit(test())
