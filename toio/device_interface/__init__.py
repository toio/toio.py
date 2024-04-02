# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/device_interface/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""device_interface

Abstraction layer to communicate toio Core Cubes.

The abstract base classes defined are as follows:

* ScannerInterface
* CubeInterface

"""

from abc import ABCMeta, abstractmethod
from typing import List, Set
from uuid import UUID

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing_extensions import (
    Awaitable,
    Callable,
    Literal,
    NamedTuple,
    Optional,
    TypeAlias,
    Union,
)

DEFAULT_SCAN_TIMEOUT = 5.0

GattReadData: TypeAlias = bytearray
GattWriteData: TypeAlias = Union[bytes, bytearray, memoryview]
GattCharacteristic: TypeAlias = BleakGATTCharacteristic
GattNotificationHandler: TypeAlias = Callable[
    [GattCharacteristic, bytearray], Union[None, Awaitable[None]]
]


class CubeInterface(metaclass=ABCMeta):
    """CubeInterface

    Interface to communicate to a toio Core Cube.
    """

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError()

    @abstractmethod
    async def connect(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def disconnect(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def read(self, char_uuid: UUID) -> GattReadData:
        raise NotImplementedError()

    @abstractmethod
    async def write(
        self, char_uuid: UUID, data: GattWriteData, response: bool = False
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def register_notification_handler(
        self, char_uuid: UUID, notification_handler: GattNotificationHandler
    ) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def unregister_notification_handler(self, char_uuid: UUID) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_connect(self) -> bool:
        """
        Implemented in v1.1.0 or later

        get current connection state
        """
        raise NotImplementedError()


CubeDevice = BLEDevice
CubeAdvertisement = AdvertisementData


class CubeInfo(NamedTuple):
    name: Optional[str]
    device: CubeDevice
    interface: CubeInterface
    advertisement: CubeAdvertisement


SortKey = Optional[Literal["rssi", "local_name"]]


class ScannerInterface(metaclass=ABCMeta):
    """ScannerInterface

    Interface to scan toio Core Cubes.
    This interface is used from toio.scanner.* module.
    """

    @abstractmethod
    async def scan(
        self,
        num: Optional[int] = None,
        cube_id: Optional[Set[str]] = None,
        address: Optional[Set[str]] = None,
        sort: SortKey = None,
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> List[CubeInfo]:
        raise NotImplementedError()
