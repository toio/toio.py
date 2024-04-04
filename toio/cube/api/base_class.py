# -*- coding: utf-8 -*-
# ************************************************************
#
#     base_class.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import binascii
from abc import ABCMeta, abstractmethod
from uuid import UUID

from typing_extensions import (
    Any,
    Dict,
    Optional,
    cast,
)

from toio.cube.notification_handler_info import (
    CubeNotificationHandler,
    CubeNotificationHandlerAsync,
    CubeNotificationHandlerWithParameter,
    CubeNotificationHandlerWithParameterAsync,
    NotificationHandlerInfo,
    NotificationHandlerTypes,
)
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
    def is_myself(payload: GattReadData) -> bool:
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

    def __init__(self, interface: CubeInterface, uuid: UUID, device: Any = None):
        self.interface = interface
        self.uuid = uuid
        self.device = device
        self.notification_handler_dict: Dict[
            NotificationHandlerTypes, NotificationHandlerInfo
        ] = {}
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
        for func, handler_info in self.notification_handler_dict.items():
            if handler_info.is_async:
                if handler_info.num_of_args == 1:
                    func = cast(CubeNotificationHandlerAsync, func)
                    await func(payload)
                elif handler_info.num_of_args == 2:
                    func = cast(CubeNotificationHandlerWithParameterAsync, func)
                    await func(payload, handler_info)
            else:
                if handler_info.num_of_args == 1:
                    func = cast(CubeNotificationHandler, func)
                    func(payload)
                elif handler_info.num_of_args == 2:
                    func = cast(CubeNotificationHandlerWithParameter, func)
                    func(payload, handler_info)

    async def register_notification_handler(
        self, handler: NotificationHandlerTypes, misc: Any = None
    ) -> bool:
        """
        User interface to GATT for registering handler function.

        Note:
            Type of the notification handler function must be
                Callable[[bytearray, ToioNotificationHandlerInfo], None]
            or
                Callable[[bytearray, ToioNotificationHandlerInfo], Awaitable[None]]

            `NotificationHandlerInfo` has `device`, `interface` and `misc` attributes.
            `device` attribute is the ToioCoreCube instance that received the notification.
            `interface` attribute is the CubeInterface instance that received the notification.
            `misc` attribute is set to the `misc` argument of this function.

            If you want to use some cube api in the notification handler, you must define
            the notification handler as async function.
            In this case, you can await the cube api in the notification handler.

        Args:
            handler (ToioCoreCubeNotificationHandler): handler function
            misc (Any): data given to the handler function as NotificationHandlerInfo.misc

        Returns:
            bool:
        """
        if handler in self.notification_handler_dict:
            return False
        handler_info = NotificationHandlerInfo(
            func=handler, misc=misc, device=self.device, interface=self.interface
        )
        self.notification_handler_dict[handler] = handler_info
        if not self.notification_handler_is_registered:
            await self._register_notification_handler(self._root_notification_handler)
            self.notification_handler_is_registered = True
        return True

    async def unregister_notification_handler(
        self,
        handler: NotificationHandlerTypes,
    ) -> bool:
        """User interface to GATT for unregistering handler function."""
        if handler is None:
            self.notification_handler_dict.clear()
            return True
        if handler in self.notification_handler_dict:
            self.notification_handler_dict.pop(handler)
        if (
            len(self.notification_handler_dict) == 0
            and self.notification_handler_is_registered
        ):
            await self._unregister_notification_handler()
            self.notification_handler_is_registered = False
        return True
