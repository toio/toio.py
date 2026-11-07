#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_scanner.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************
#
# Two cubes are required for this test.
# This test is performed on the cubes listed in _cubes.py.
# Before testing, turn on the cubes, run make_cube_list.py and
# save the output as _cubes.py.
# On Windows, register those two cubes as Bluetooth devices to the OS.
#

import platform
import pprint
from logging import getLogger

import pytest

from toio.scanner import BLEScanner

logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_rssi(cubes):
    logger.info("** RSSI")
    dev = await BLEScanner.scan(len(cubes))
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == len(cubes)


@pytest.mark.asyncio
async def test_local_name(cubes):
    logger.info("** LOCAL NAME")
    dev = await BLEScanner.scan(len(cubes), sort="local_name")
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == len(cubes)


@pytest.mark.asyncio
async def test_num1():
    logger.info("** NUM1")
    dev = await BLEScanner.scan(num=1)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 1


@pytest.mark.asyncio
async def test_name1(cubes):
    logger.info("** NAME1")
    dev = await BLEScanner.scan_with_id(cube_id={cubes[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 1


@pytest.mark.asyncio
async def test_name2(cubes):
    logger.info("** NAME2")
    dev = await BLEScanner.scan_with_id(cube_id={cubes[0]["name"], cubes[1]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 2


@pytest.mark.asyncio
async def test_name3(cubes):
    logger.info("** NAME3")
    dev = await BLEScanner.scan_with_id(
        cube_id={cubes[0]["name"], cubes[1]["name"], cubes[0]["name"]}
    )
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 2


@pytest.mark.asyncio
async def test_address1(cubes):
    logger.info("** ADDRESS1 (UPPERCASE)")
    dev = await BLEScanner.scan_with_address(address={cubes[0]["address"].upper()})
    for d in dev:
        logger.info(d)
        assert len(dev) == 1


@pytest.mark.asyncio
async def test_address2(cubes):
    logger.info("** ADDRESS2 (LOWERCASE)")
    dev = await BLEScanner.scan_with_address(address={cubes[0]["address"].lower()})
    for d in dev:
        logger.info(d)
        assert len(dev) == 1


@pytest.mark.asyncio
async def test_registered_1():
    logger.info("** REGISTERED1")
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
    logger.info("** REGISTERED2")
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
    logger.info("** REGISTERED3")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo"})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_4(cubes):
    logger.info("** REGISTERED4")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo", cubes[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    if platform.system() == "Windows":
        assert len(dev) == 1
    else:
        logger.info("scan_registered_cubes() is not supported on %s", platform.system())
        assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_5(mocker):
    logger.info("** REGISTERED5")
    mocker.patch("platform.system", return_value="UnknownOS")
    dev = await BLEScanner.scan_registered_cubes(1)
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0


@pytest.mark.asyncio
async def test_registered_6(mocker, cubes):
    logger.info("** REGISTERED6")
    mocker.patch("platform.system", return_value="UnknownOS")
    dev = await BLEScanner.scan_registered_cubes_with_id({"ooo", cubes[0]["name"]})
    for d in dev:
        pprint.pprint(d)
    assert len(dev) == 0
