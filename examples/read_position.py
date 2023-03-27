#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     read_position.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
Display id information on the console.

This example uses:
 * notification handler to receive id information
 * signal handler to catch Ctrl-C
"""

import asyncio
import signal
import sys

from toio.cube import IdInformation, ToioCoreCube
from toio.scanner import BLEScanner


def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))


LOOP = True


def ctrl_c_handler(_signum, _frame):
    global LOOP
    print("Ctrl-C")
    LOOP = False


# Add signal handler
signal.signal(signal.SIGINT, ctrl_c_handler)


async def read_id():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    # add notification handler
    await cube.api.id_information.register_notification_handler(notification_handler)
    try:
        # Loop until Ctrl-C is pressed
        while LOOP:
            await asyncio.sleep(0.1)
    finally:
        # remove notification handler
        await cube.api.id_information.unregister_notification_handler(
            notification_handler
        )
        await cube.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(read_id()))
