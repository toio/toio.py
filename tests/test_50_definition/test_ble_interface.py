#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_ble_interface.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pytest

from toio.device_interface.ble import BleCube


class FakeBleakClient:
    def __init__(self, *args, **kwargs):
        self.is_connected = False
        self.connect_calls = 0
        self.disconnect_calls = 0

    async def connect(self):
        self.connect_calls += 1
        self.is_connected = True
        return None

    async def disconnect(self):
        self.disconnect_calls += 1
        self.is_connected = False
        return None


@pytest.mark.asyncio
async def test_ble_cube_connect_disconnect_with_none_return(mocker):
    mocker.patch("toio.device_interface.ble.BleakClient", FakeBleakClient)

    cube = BleCube("dummy")

    assert cube.connected is False
    assert cube.is_connect() is False

    result = await cube.connect()

    assert result is True
    assert cube.connected is True
    assert cube.is_connect() is True
    assert cube.device.connect_calls == 1

    result = await cube.disconnect()

    assert result is True
    assert cube.connected is False
    assert cube.is_connect() is False
    assert cube.device.disconnect_calls == 1


@pytest.mark.asyncio
async def test_ble_cube_reconnect_and_redisconnect_are_idempotent(mocker):
    mocker.patch("toio.device_interface.ble.BleakClient", FakeBleakClient)

    cube = BleCube("dummy")

    await cube.connect()
    await cube.connect()

    assert cube.connected is True
    assert cube.is_connect() is True
    assert cube.device.connect_calls == 1

    await cube.disconnect()
    await cube.disconnect()

    assert cube.connected is False
    assert cube.is_connect() is False
    assert cube.device.disconnect_calls == 1
