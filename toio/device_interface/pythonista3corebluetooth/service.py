"""
Port to Pythonista3 by Sony Interactive Entertainment Inc.

"""

import logging
from typing import List

from bleak.backends.service import BleakGATTService

from .characteristic import BleakGATTCharacteristicPythonista3
from .objc_types import CBService, CBServiceType
from .utils import cb_uuid_to_str

logger = logging.getLogger(__name__)


class BleakGATTServicePythonista3(BleakGATTService):
    """GATT Characteristic implementation for the CoreBluetooth backend"""

    def __init__(self, obj: CBServiceType):
        super().__init__(obj)
        self.__characteristics: List[BleakGATTCharacteristicPythonista3] = []
        # N.B. the `startHandle` method of the CBService is an undocumented Core Bluetooth feature,
        # which Bleak takes advantage of in order to have a service handle to use.
        handle = self.obj.startHandle()
        self.__handle: int = int(str(handle))

    @property
    def handle(self) -> int:
        """The integer handle of this service"""
        return self.__handle

    @property
    def uuid(self) -> str:
        """UUID for this service."""
        return cb_uuid_to_str(self.obj.UUID())

    @property
    def characteristics(self) -> List[BleakGATTCharacteristicPythonista3]:
        """List of characteristics for this service"""
        return self.__characteristics

    def add_characteristic(self, characteristic: BleakGATTCharacteristicPythonista3):
        """Add a :py:class:`~BleakGATTCharacteristicCoreBluetooth` to the service.

        Should not be used by end user, but rather by `bleak` itself.
        """
        self.__characteristics.append(characteristic)
