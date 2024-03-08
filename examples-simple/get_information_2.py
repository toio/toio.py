#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     get_information_2.py
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
            angle = cube.get_3d_angle()
            posture = cube.get_posture()
            magnet = cube.is_magnet_in_contact()

            print("ANGLE:", angle, "POSTURE:", posture, "MAGNET", magnet)

            if cube.is_button_pressed():
                print("exit")
                break
            cube.sleep(0.5)

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
