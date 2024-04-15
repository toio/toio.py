"""
Interface class for the Bleak representation of a GATT Descriptor

Created on 2019-06-28 by kevincar <kevincarrolldavis@gmail.com>

Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

from bleak.backends.descriptor import BleakGATTDescriptor
from objc_util import nsdata_to_bytes

from .objc_types import CBDescriptor, CBDescriptorType
from .utils import cb_uuid_to_str


class BleakGATTDescriptorPythonista3(BleakGATTDescriptor):
    """GATT Descriptor implementation for CoreBluetooth backend"""

    def __init__(
        self,
        obj: CBDescriptorType,
        characteristic_uuid: str,
        characteristic_handle: int,
    ):
        super(BleakGATTDescriptorPythonista3, self).__init__(obj)
        self.obj: CBDescriptorType = obj
        self.__characteristic_uuid: str = characteristic_uuid
        self.__characteristic_handle: int = characteristic_handle

    @property
    def characteristic_handle(self) -> int:
        """handle for the characteristic that this descriptor belongs to"""
        return self.__characteristic_handle

    @property
    def characteristic_uuid(self) -> str:
        """UUID for the characteristic that this descriptor belongs to"""
        return self.__characteristic_uuid

    @property
    def uuid(self) -> str:
        """UUID for this descriptor"""
        return cb_uuid_to_str(self.obj.UUID())

    @property
    def handle(self) -> int:
        """Integer handle for this descriptor"""
        return int(str(self.obj.handle()))
