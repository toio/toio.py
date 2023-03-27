#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     scan_and_connect.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
Scan and connect a toio Core Cube.

Disconnect 3 seconds after connecting.
"""

import asyncio
import sys

from toio.cube import ToioCoreCube
from toio.scanner import BLEScanner


async def scan_and_connect():
    print("scan")
    dev_list = await BLEScanner.scan(num=1)

    print("complete to scan")
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)

    print("connecting...")
    await cube.connect()
    print("connected")

    await asyncio.sleep(3)

    print("disconnecting...")
    await cube.disconnect()
    print("disconnected")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(scan_and_connect()))
