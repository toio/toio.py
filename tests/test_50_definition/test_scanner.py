#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_scanner.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from contextlib import suppress
from types import SimpleNamespace

import pytest

from toio.device_interface.ble import BaseBleScanner
from toio.scanner.ble import UniversalBleScanner
from toio.toio_uuid import TOIO_UUID_SERVICE


class FakeBleakScanner:
    entries = ()
    interval = 0.02

    def __init__(self, detection_callback, backend=None):
        self._callback = detection_callback
        self._task = None

    async def __aenter__(self):
        async def emit():
            for device, advertisement in self.entries:
                await asyncio.sleep(self.interval)
                self._callback(device, advertisement)

        self._task = asyncio.create_task(emit())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._task is not None and not self._task.done():
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task


def make_entry(address: str, name: str, rssi: int):
    device = SimpleNamespace(address=address, name=name)
    advertisement = SimpleNamespace(service_uuids=[str(TOIO_UUID_SERVICE)], rssi=rssi)
    return device, advertisement


@pytest.mark.asyncio
async def test_base_ble_scanner_strategy_best_collects_until_timeout(mocker):
    FakeBleakScanner.entries = (
        make_entry("A1", "cube-a", -70),
        make_entry("A2", "cube-b", -60),
        make_entry("A3", "cube-c", -10),
    )
    mocker.patch("toio.device_interface.ble.BleakScanner", FakeBleakScanner)
    mocker.patch("toio.device_interface.ble.BleCube", side_effect=lambda device: device)

    scanner = BaseBleScanner()
    # Far above the 0.06 s the three detections need: Windows timer granularity
    # can stretch each 0.02 s sleep, and a tight timeout drops the last cube.
    cubes = await scanner._scan(num=2, sort="rssi", timeout=0.5, strategy="best")

    assert [cube.device.address for cube in cubes] == ["A3", "A2"]


@pytest.mark.asyncio
async def test_base_ble_scanner_strategy_quick_returns_early(mocker):
    FakeBleakScanner.entries = (
        make_entry("A1", "cube-a", -70),
        make_entry("A2", "cube-b", -60),
        make_entry("A3", "cube-c", -10),
    )
    mocker.patch("toio.device_interface.ble.BleakScanner", FakeBleakScanner)
    mocker.patch("toio.device_interface.ble.BleCube", side_effect=lambda device: device)

    scanner = BaseBleScanner()
    cubes = await scanner._scan(num=2, sort="rssi", timeout=0.5, strategy="quick")

    assert [cube.device.address for cube in cubes] == ["A2", "A1"]


@pytest.mark.asyncio
async def test_base_ble_scanner_rejects_unknown_strategy():
    scanner = BaseBleScanner()

    with pytest.raises(ValueError, match="wrong strategy"):
        await scanner._scan(num=1, timeout=0.01, strategy="unknown")


@pytest.mark.asyncio
async def test_universal_ble_scanner_scan_best_calls_best_strategy(mocker):
    scan_mock = mocker.patch(
        "toio.scanner.ble.UniversalBleScanner._scan",
        return_value=[],
    )

    scanner = UniversalBleScanner()
    await scanner.scan_best(num=1, timeout=1.0)

    scan_mock.assert_awaited_once_with(num=1, sort="rssi", timeout=1.0, strategy="best")


@pytest.mark.asyncio
async def test_universal_ble_scanner_scan_quick_calls_quick_strategy(mocker):
    scan_mock = mocker.patch(
        "toio.scanner.ble.UniversalBleScanner._scan",
        return_value=[],
    )

    scanner = UniversalBleScanner()
    await scanner.scan_quick(num=1, timeout=1.0)

    scan_mock.assert_awaited_once_with(
        num=1, sort="rssi", timeout=1.0, strategy="quick"
    )
