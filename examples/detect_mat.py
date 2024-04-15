#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     detect_mat.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
Detect mat type.
"""

import asyncio
import signal
import sys

from toio import *


def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    if isinstance(id_info, PositionId):
        point = id_info.center.point
        for mat in ToioMat.mats:
            if point in mat:
                print(str(mat))
    print(str(id_info))


LOOP = True


def ctrl_c_handler(_signum, _frame):
    global LOOP
    print("Ctrl-C")
    LOOP = False


# Add signal handler
signal.signal(signal.SIGINT, ctrl_c_handler)


async def read_id():
    async with ToioCoreCube() as cube:
        # add notification handler
        await cube.api.id_information.register_notification_handler(
            notification_handler
        )
        try:
            # Loop until Ctrl-C is pressed
            while LOOP:
                await asyncio.sleep(0.1)
        finally:
            # remove notification handler
            await cube.api.id_information.unregister_notification_handler(
                notification_handler
            )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(read_id()))
