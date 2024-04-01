# -*- coding: utf-8 -*-
# ************************************************************
#
#     dummy.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
Dummy device interface (for debugging)
"""

from uuid import UUID

from toio.device_interface import (
    CubeInterface,
    GattNotificationHandler,
    GattReadData,
    GattWriteData,
)


class DummyCube(CubeInterface):
    """
    Dummy cube interface for debugging.

    All functions succeed but do nothing.
    read() returns empty list '[]'.
    """

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> bool:
        return True

    async def read(self, uuid: UUID) -> GattReadData:
        return GattReadData([])

    async def write(
        self, uuid: UUID, data: GattWriteData, response: bool = False
    ) -> None:
        pass

    async def register_notification_handler(
        self, uuid: UUID, handler: GattNotificationHandler
    ) -> bool:
        return True

    async def unregister_notification_handler(self, uuid: UUID) -> bool:
        return True
