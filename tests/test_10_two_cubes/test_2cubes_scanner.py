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
import time
from logging import getLogger

import pytest

from toio.scanner import BLEScanner

logger = getLogger(__name__)

REQUIRED_CUBES = 2
STRATEGY_BEST_TIMEOUT = 3.0
STRATEGY_QUICK_TIMEOUT = 20.0
# A timer can fire slightly early on a coarse clock such as the one on Windows.
TIMER_MARGIN = 0.1


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


async def scan_and_measure(scan_function, *args, **kwargs):
    start = time.monotonic()
    dev = await scan_function(*args, **kwargs)
    elapsed = time.monotonic() - start
    for d in dev:
        pprint.pprint(d)
    logger.info("elapsed: %.2f sec", elapsed)
    return dev, elapsed


@pytest.mark.asyncio
@pytest.mark.parametrize("num", [1, REQUIRED_CUBES])
async def test_strategy_best_scans_until_timeout(num):
    logger.info("** STRATEGY BEST (%d)", num)
    dev, elapsed = await scan_and_measure(
        BLEScanner.scan, num, timeout=STRATEGY_BEST_TIMEOUT, strategy="best"
    )
    assert len(dev) == num
    assert elapsed >= STRATEGY_BEST_TIMEOUT - TIMER_MARGIN


@pytest.mark.asyncio
@pytest.mark.parametrize("num", [1, REQUIRED_CUBES])
async def test_strategy_quick_returns_before_timeout(num):
    logger.info("** STRATEGY QUICK (%d)", num)
    dev, elapsed = await scan_and_measure(
        BLEScanner.scan, num, timeout=STRATEGY_QUICK_TIMEOUT, strategy="quick"
    )
    assert len(dev) == num
    assert elapsed < STRATEGY_QUICK_TIMEOUT


@pytest.mark.asyncio
async def test_strategy_best_is_default(cubes):
    logger.info("** STRATEGY DEFAULT")
    dev, elapsed = await scan_and_measure(
        BLEScanner.scan, len(cubes), timeout=STRATEGY_BEST_TIMEOUT
    )
    assert len(dev) == len(cubes)
    assert elapsed >= STRATEGY_BEST_TIMEOUT - TIMER_MARGIN


@pytest.mark.asyncio
async def test_strategy_best_sorts_by_rssi(cubes):
    logger.info("** STRATEGY BEST (RSSI)")
    dev, _ = await scan_and_measure(
        BLEScanner.scan, len(cubes), timeout=STRATEGY_BEST_TIMEOUT, strategy="best"
    )
    assert len(dev) == len(cubes)
    rssi = [d.advertisement.rssi for d in dev]
    assert rssi == sorted(rssi, reverse=True)


@pytest.mark.asyncio
async def test_scan_best(cubes):
    logger.info("** SCAN BEST")
    dev, elapsed = await scan_and_measure(
        BLEScanner.scan_best, len(cubes), timeout=STRATEGY_BEST_TIMEOUT
    )
    assert len(dev) == len(cubes)
    assert elapsed >= STRATEGY_BEST_TIMEOUT - TIMER_MARGIN


@pytest.mark.asyncio
async def test_scan_quick(cubes):
    logger.info("** SCAN QUICK")
    dev, elapsed = await scan_and_measure(
        BLEScanner.scan_quick, len(cubes), timeout=STRATEGY_QUICK_TIMEOUT
    )
    assert len(dev) == len(cubes)
    assert elapsed < STRATEGY_QUICK_TIMEOUT


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
