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
    Optional,
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
    def __init__(
        self,
        func: NotificationHandlerTypes,
        misc: Any = None,
        device: Optional[NotificationReceivedDevice] = None,
        interface: Optional[CubeInterface] = None,
    ):
        self._misc: Any = misc
        self._device: Optional[NotificationReceivedDevice] = device
        self._interface: Optional[CubeInterface] = interface
        self._is_async: bool = inspect.iscoroutinefunction(func)
        self._num_of_args = len(inspect.signature(func).parameters)

    @property
    def misc(self):
        return self._misc

    @property
    def device(self):
        return self._device

    @property
    def interface(self):
        return self._interface

    @property
    def is_async(self):
        return self._is_async

    @property
    def num_of_args(self):
        return self._num_of_args

    def get_notified_cube(self) -> ToioCoreCube:
        from toio.cube import ToioCoreCube

        return cast(ToioCoreCube, self.device)
