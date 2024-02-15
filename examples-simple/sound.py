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

        cube.play_sound(note=60, duration=3, wait_to_complete=False)
        print("pp-- 2.55[s]")
        cube.sleep(2.55)
        print("stop")
        cube.sleep(1)
        print("pp-- 0.5[s]")
        cube.play_sound(note=60, duration=3, wait_to_complete=False)
        cube.sleep(0.5)
        cube.stop_sound()
        print("stop")
        print("wait 3 sec")
        cube.sleep(3)
        print("disconnecting")

    print("** DISCONNECTED")
    print("** END")


if __name__ == "__main__":
    sys.exit(test())
