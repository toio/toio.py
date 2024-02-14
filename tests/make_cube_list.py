#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     make_cube_list.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
import sys
from typing import Dict, List

from toio.scanner import BLEScanner

CUBES: List[Dict[str, str]] = [
    {"name": "31j", "address": "DD:14:33:3D:14:0F"},
    {"name": "h7p", "address": "D8:E3:49:A0:EF:19"},
]


async def main(argv):
    dev = await BLEScanner.scan(2)
    if len(dev) < 2:
        print("failed to find 2 cubes")
        sys.exit(1)

    print("from typing import Dict, List")
    print()
    print("CUBES: List[Dict[str, str]] = [")
    for d in dev:
        print(f'    {{"name": "{d.device.name}", "address": "{d.device.address}"}},')
    print("]")


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv)))
