#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_toio_core_cube.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

from types import SimpleNamespace

import pytest

from toio.cube import ToioCoreCube
from toio.device_interface import CubeInfo
from toio.device_interface.dummy import DummyCube


class TrackingDummyCube(DummyCube):
    def __init__(self):
        self.connect_count = 0
        self.disconnect_count = 0

    async def connect(self) -> bool:
        self.connect_count += 1
        return True

    async def disconnect(self) -> bool:
        self.disconnect_count += 1
        return True

    async def read(self, char_uuid):
        # Report the protocol version the library targets, so bumping
        # SUPPORTED_MINOR_VERSION does not make connect() warn here.
        version = "%d.%d.0" % (
            ToioCoreCube.SUPPORTED_MAJOR_VERSION,
            ToioCoreCube.SUPPORTED_MINOR_VERSION,
        )
        return bytearray((0x81, 0x00)) + version.encode()


@pytest.mark.asyncio
async def test_init_with_cube_info():
    interface = TrackingDummyCube()
    cube_info = CubeInfo(
        name="dummy",
        device=SimpleNamespace(address="00:00:00:00:00:00", name="dummy"),
        interface=interface,
        advertisement=SimpleNamespace(rssi=-42),
    )

    cube = ToioCoreCube(cube_info)

    assert cube.interface is interface
    assert cube.name == "dummy"

    await cube.connect()
    await cube.disconnect()

    assert interface.connect_count == 1
    assert interface.disconnect_count == 1


def test_init_with_cube_info_and_explicit_name():
    interface = TrackingDummyCube()
    cube_info = CubeInfo(
        name="dummy",
        device=SimpleNamespace(address="00:00:00:00:00:00", name="dummy"),
        interface=interface,
        advertisement=SimpleNamespace(rssi=-42),
    )

    cube = ToioCoreCube(cube_info, name="override")

    assert cube.interface is interface
    assert cube.name == "override"
