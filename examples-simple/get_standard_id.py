#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     get_standard_id.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import signal
import sys

from toio.simple import SimpleCube
from toio.standard_id import StandardIdCard

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
            card = cube.get_touched_card()
            print("CARD:", card)

            touched_zero = cube.is_touched(StandardIdCard.NUMBER_0)
            if touched_zero:
                print("ZERO! (exit)")
                break

            cube.sleep(0.5)

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
