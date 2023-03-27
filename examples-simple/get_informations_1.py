#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     get_informations_1.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import signal
import sys

from toio.simple import SimpleCube

LOOP = True


def ctrl_c_handler(_signum, _frame):
    global LOOP
    print("Ctrl-C")
    LOOP = False


signal.signal(signal.SIGINT, ctrl_c_handler)


def test():
    print("** ACTIVATE")
    with SimpleCube() as cube:
        print("** CONNECTED")
        print("CUBE NAME:", cube.get_cube_name())

        while LOOP:
            pos = cube.get_current_position()
            x = cube.get_x()
            y = cube.get_y()
            orientation = cube.get_orientation()

            grid = cube.get_grid()
            grid_x = cube.get_grid_x()
            grid_y = cube.get_grid_y()

            battery_level = cube.get_battery_level()

            button_state = cube.is_button_pressed()

            print(
                "POSITION:",
                pos,
                x,
                y,
                orientation,
                "GRID:",
                grid,
                grid_x,
                grid_y,
                "BATTERY",
                battery_level,
                "BUTTON",
                button_state,
            )

            if cube.is_button_pressed():
                print("exit")
                break

            cube.sleep(0.5)

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
