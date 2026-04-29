#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_configuration.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

from uuid import UUID

import pytest

from toio.cube.api.configuration import Configuration


class FakeCubeInterface:
    def __init__(self) -> None:
        self.writes = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> bool:
        return True

    async def read(self, char_uuid: UUID) -> bytearray:
        raise NotImplementedError()

    async def write(self, char_uuid: UUID, data, response: bool = False) -> None:
        self.writes.append((char_uuid, bytes(data), response))

    async def register_notification_handler(self, char_uuid: UUID, notification_handler) -> bool:
        return True

    async def unregister_notification_handler(self, char_uuid: UUID) -> bool:
        return True

    def is_connect(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_set_collision_detection_threshold_writes_collision_command():
    interface = FakeCubeInterface()
    configuration = Configuration(interface, device=None)

    await configuration.set_collision_detection_threshold(7)

    assert len(interface.writes) == 1
    char_uuid, data, response = interface.writes[0]
    assert char_uuid == configuration.uuid
    assert data == bytes((0x06, 0x00, 0x07))
    assert response is True
