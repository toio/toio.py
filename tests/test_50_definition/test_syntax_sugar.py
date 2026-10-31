#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_syntax_sugar.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pytest

from toio.cube import MultipleToioCoreCubes, ToioCoreCube
from toio.scanner.ble import UniversalBleScanner


@pytest.mark.asyncio
async def test_toio_core_cube_passes_keyword_arguments_to_scanner(mocker):
    scan_mock = mocker.patch.object(UniversalBleScanner, "scan", return_value=[])

    cube = ToioCoreCube(strategy="quick", timeout=1.23, sort="local_name")
    await cube.scan()

    scan_mock.assert_called_once_with(
        1, strategy="quick", timeout=1.23, sort="local_name"
    )


@pytest.mark.asyncio
async def test_multiple_toio_core_cubes_passes_keyword_arguments_to_scanner(mocker):
    scan_mock = mocker.patch.object(UniversalBleScanner, "scan", return_value=[])

    cubes = MultipleToioCoreCubes(2, strategy="best", timeout=5.0)
    await cubes.scan()

    scan_mock.assert_called_once_with(2, strategy="best", timeout=5.0)


@pytest.mark.asyncio
async def test_scanner_args_and_keyword_arguments_are_combined(mocker):
    scan_mock = mocker.patch.object(UniversalBleScanner, "scan", return_value=[])

    # scanner_args is forwarded positionally, after the cube count
    cube = ToioCoreCube(scanner_args=("rssi", 10.0), strategy="quick")
    await cube.scan()

    scan_mock.assert_called_once_with(1, "rssi", 10.0, strategy="quick")
