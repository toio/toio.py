# -*- coding: utf-8 -*-
# ************************************************************
#
#     notification_handler_info.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import inspect

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    TypeAlias,
    Union,
    cast,
)

from ..device_interface import CubeInterface

if TYPE_CHECKING:
    from toio.cube import ToioCoreCube

CubeNotificationHandler: TypeAlias = Callable[[bytearray], None]
CubeNotificationHandlerAsync: TypeAlias = Callable[[bytearray], Awaitable[None]]
CubeNotificationHandlerWithParameter: TypeAlias = Callable[[bytearray, Any], None]
CubeNotificationHandlerWithParameterAsync: TypeAlias = Callable[
    [bytearray, Any], Awaitable[None]
]

NotificationHandlerTypes: TypeAlias = Union[
    CubeNotificationHandler,
    CubeNotificationHandlerAsync,
    CubeNotificationHandlerWithParameter,
    CubeNotificationHandlerWithParameterAsync,
]

NotificationReceivedDevice: TypeAlias = Any


class NotificationHandlerInfo:
    """
    Information of registered notification handler function.

    NotificationHandlerInfo includes several type of information:
        - Unique data given at registration (misc)
        - Information about the device that received the notification (device, interface)
        - Information used for internal use (rest of properties)
    """

    def __init__(
        self,
        func: NotificationHandlerTypes,
        device: NotificationReceivedDevice,
        interface: CubeInterface,
        misc: Any = None,
    ):
        """__init__.

        Args:
            func (NotificationHandlerTypes): notification handler function
            device (NotificationReceivedDevice): device to be notified
            interface (CubeInterface): interface of device
            misc (Any): user data
        """
        self._device: NotificationReceivedDevice = device
        self._interface: CubeInterface = interface
        self._misc: Any = misc
        self._is_async: bool = inspect.iscoroutinefunction(func)
        self._num_of_args = len(inspect.signature(func).parameters)

    @property
    def misc(self) -> Any:
        """
        User data given when the notification handler function is registered.
        """
        return self._misc

    @property
    def device(self) -> NotificationReceivedDevice:
        """
        The device that received the notification.
        """
        return self._device

    @property
    def interface(self) -> CubeInterface:
        """
        The interface of the device that received the notification. (equal to device.interface)
        """
        return self._interface

    @property
    def is_async(self) -> bool:
        """
        Whether the notification handler function is async or sync. (for internal use)
        """
        return self._is_async

    @property
    def num_of_args(self) -> int:
        """
        Number of arguments received by the registered notification handler function. (for internal use)
        """
        return self._num_of_args

    def get_notified_cube(self) -> ToioCoreCube:
        """
        Return self.device as ToioCoreCube
        """
        from toio.cube import ToioCoreCube

        return cast(ToioCoreCube, self.device)
