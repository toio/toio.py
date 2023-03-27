#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_scanner.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import platform
import pprint
from logging import getLogger

import pytest

from toio.scanner import BLEScanner

logger = getLogger(__name__)


CUBES: list[dict[str, str]] = [
    {"name": "31j", "address": "DD:14:33:3D:14:0F"},
    {"name": "h7p", "address": "D8:E3:49:A0:EF:19"},
]


@pytest.mark.asyncio
async def test_rssi():
    print("** RSSI")
    dev = await BLEScanner.scan(len(CUBES))
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == len(CUBES)


@pytest.mark.asyncio
async def test_local_name():
    print("** LOCAL NAME")
    dev = await BLEScanner.scan(len(CUBES), sort="local_name")
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == len(CUBES)


@pytest.mark.asyncio
async def test_num1():
    print("** NUM1")
    dev = await BLEScanner.scan(num=1)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 1


@pytest.mark.asyncio
async def test_name1():
    print("** NAME1")
    dev = await BLEScanner.scan_with_id(cube_id={CUBES[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 1


@pytest.mark.asyncio
async def test_name2():
    print("** NAME2")
    dev = await BLEScanner.scan_with_id(cube_id={CUBES[0]["name"], CUBES[1]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 2


@pytest.mark.asyncio
async def test_name3():
    print("** NAME3")
    dev = await BLEScanner.scan_with_id(
        cube_id={CUBES[0]["name"], CUBES[1]["name"], CUBES[0]["name"]}
    )
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 2


@pytest.mark.asyncio
async def test_address1():
    print("** ADDRESS1 (UPPERCASE)")
    dev = await BLEScanner.scan_with_address(address={CUBES[0]["address"].upper()})
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Darwin":
        assert len(dev) == 0
    else:
        assert len(dev) == 1


@pytest.mark.asyncio
async def test_address2():
    print("** ADDRESS2 (LOWERCASE)")
    dev = await BLEScanner.scan_with_address(address={CUBES[0]["address"].lower()})
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Darwin":
        assert len(dev) == 0
    else:
        assert len(dev) == 1


@pytest.mark.asyncio
async def test_registered_1():
    print("** REGISTERED1")
    dev = await BLEScanner.scan_registered_cubes(1)
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Windows":
        assert len(dev) == 1
    else:
        logger.info("scan_registered_cubes() is not supported on %s", platform.system())
        assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_2():
    print("** REGISTERED2")
    dev = await BLEScanner.scan_registered_cubes(2)
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Windows":
        assert len(dev) == 2
    else:
        logger.info("scan_registered_cubes() is not supported on %s", platform.system())
        assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_3():
    print("** REGISTERED3")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo"})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_4():
    print("** REGISTERED4")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo", CUBES[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Windows":
        assert len(dev) == 1
    else:
        logger.info("scan_registered_cubes() is not supported on %s", platform.system())
        assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_5(mocker):
    print("** REGISTERED5")
    mocker.patch("platform.system", return_value="UnknownOS")
    dev = await BLEScanner.scan_registered_cubes(1)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_6(mocker):
    print("** REGISTERED6")
    mocker.patch("platform.system", return_value="UnknownOS")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo", CUBES[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0
