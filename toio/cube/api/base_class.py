# -*- coding: utf-8 -*-
# ************************************************************
#
#     base_class.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import binascii
import inspect
from abc import ABCMeta, abstractmethod
from typing import Awaitable, Callable, Optional, Union
from uuid import UUID

from toio.device_interface import (
    CubeInterface,
    GattCharacteristic,
    GattNotificationHandler,
    GattReadData,
    GattWriteData,
)
from toio.logger import get_toio_logger

logger = get_toio_logger(__name__)

DUMP_RAW_READ_DATA = False
DUMP_RAW_WRITE_DATA = False

CubeNotificationHandler = Callable[[bytearray], Union[None, Awaitable[None]]]


class CubeCommand(metaclass=ABCMeta):
    @abstractmethod
    def __bytes__(self) -> bytes:
        """Returns the byte representation of this class to be sent to cube.

        Returns:
            bytes: byte representation of this class to be sent to cube.
        """
        raise NotImplementedError()


class CubeResponse(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def is_myself(data: GattReadData) -> bool:
        """If argument data is a byte representation of this class,
        this function converts the byte representation to an object
        and returns it.

        Args:
            data (GattReadData): received data from the cube.
        """
        raise NotImplementedError()


class CubeCharacteristic(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def is_my_data(payload: GattReadData) -> Optional[CubeResponse]:
        """If payload is my characteristic response, this function returns
        CubeResponse object. Otherwise, it returns None.

        Args:
            payload (GattReadData): received data from the cube.
        """
        raise NotImplementedError()

    def __init__(self, interface: CubeInterface, uuid: UUID):
        self.interface = interface
        self.uuid = uuid
        self.notification_handler_list: list = []
        self.notification_handler_is_registered = False

    async def _read(self) -> GattReadData:
        """Raw interface to GATT for reading."""
        read_data = await self.interface.read(self.uuid)
        if DUMP_RAW_READ_DATA:
            logger.debug("READ: %s", binascii.hexlify(bytes(read_data), " "))
        return read_data

    async def _write(self, data: GattWriteData) -> None:
        """Raw interface to GATT for writing."""
        if DUMP_RAW_WRITE_DATA:
            logger.debug("WRITE: %s", binascii.hexlify(bytes(data), " "))
        return await self.interface.write(self.uuid, data, response=True)

    async def _write_without_response(self, data: GattWriteData) -> None:
        """Raw interface to GATT for writing. (without response)"""
        if DUMP_RAW_WRITE_DATA:
            logger.debug(
                "WRITE WITHOUT RESPONSE: %s", binascii.hexlify(bytes(data), " ")
            )
        return await self.interface.write(self.uuid, data, response=False)

    async def _register_notification_handler(
        self, handler: GattNotificationHandler
    ) -> bool:
        """Raw interface to GATT for registering handler function."""
        return await self.interface.register_notification_handler(self.uuid, handler)

    async def _unregister_notification_handler(self) -> bool:
        """Raw interface to GATT for unregistering handler function."""
        return await self.interface.unregister_notification_handler(self.uuid)

    async def _root_notification_handler(
        self, _: GattCharacteristic, payload: bytearray
    ) -> None:
        for handler in self.notification_handler_list:
            if inspect.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)

    async def register_notification_handler(
        self, handler: CubeNotificationHandler
    ) -> bool:
        """User interface to GATT for registering handler function."""
        if handler in self.notification_handler_list:
            return False
        self.notification_handler_list.append(handler)
        if not self.notification_handler_is_registered:
            await self._register_notification_handler(self._root_notification_handler)
            self.notification_handler_is_registered = True
        return True

    async def unregister_notification_handler(
        self, handler: Optional[CubeNotificationHandler]
    ) -> bool:
        """User interface to GATT for unregistering handler function."""
        if handler is None:
            self.notification_handler_list = []
            return True
        if handler in self.notification_handler_list:
            self.notification_handler_list.remove(handler)
        if (
            len(self.notification_handler_list) == 0
            and self.notification_handler_is_registered
        ):
            await self._unregister_notification_handler()
            self.notification_handler_is_registered = False
        return True
