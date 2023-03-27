#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     sound.py
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
        print("CUBE NAME:", cube.get_cube_name())

        cube.play_sound(note=60, duration=50, wait_to_complete=False)
        print("pp--")
        cube.sleep(1)
        print("stop")
        cube.stop_sound()
        print("wait 10 sec")
        cube.sleep(10)
        print("disconnecting")

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
