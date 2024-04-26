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


async def scan_and_connect():
    print("connecting...")
    async with ToioCoreCube() as _cube:
        print("connected")
        await asyncio.sleep(3)
        print("disconnecting...")
    print("disconnected")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(scan_and_connect()))
