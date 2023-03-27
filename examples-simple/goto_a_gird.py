#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     goto_a_cell.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import random
import sys

from toio.simple import SimpleCube


def test():
    print("** ACTIVATE")
    success = True
    with SimpleCube(timeout=3) as cube:
        print("** CONNECTED")
        while success:
            (target_cell_x, target_cell_y) = (
                random.randint(-3, 3),
                random.randint(-2, 2),
            )
            print(f"move to ({target_cell_x}, {target_cell_y})")
            success = cube.move_to_the_grid_cell(
                speed=50, cell_x=target_cell_x, cell_y=target_cell_y
            )
            print(f"result of move_to_grid_cell: {success}")
            success = cube.is_on_the_gird_cell(
                cell_x=target_cell_x, cell_y=target_cell_y
            )
            print(f"result of is_on_the_grid_cell: {success}")
            cube.sleep(1)
    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
