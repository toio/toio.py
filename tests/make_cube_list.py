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
        sys.stderr.write("failed to find 2 cubes\n")
        return 1
    else:
        if len(argv) >= 2:
            wfh = open(argv[1], "w")
        else:
            wfh = sys.stdout
        sys.stderr.write("generate cube list: '%s'\n" % argv[1])
        wfh.write("from typing import Dict, List\n")
        wfh.write("\n")
        wfh.write("CUBES: List[Dict[str, str]] = [\n")
        for d in dev:
            wfh.write(
                f'    {{"name": "{d.device.name}", "address": "{d.device.address}"}},\n'
            )
        wfh.write("]\n")
        wfh.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv)))
