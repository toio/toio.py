"""
Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

from typing import Any, Optional
from uuid import UUID

from objc_util import NSData, ObjCClass, nsdata_to_bytes
from typing_extensions import TypeAlias

CBUUID = ObjCClass("CBUUID")
CBUUIDType: TypeAlias = ObjCClass

from bleak.uuids import normalize_uuid_16, normalize_uuid_str

# Most descriptors are returned as NSData, but CoreBluetooth returns these as
# NSNumber or NSString.
# See: https://developer.apple.com/documentation/corebluetooth/characteristic-descriptors
_DESCRIPTOR_TYPE_NSNUMBER = (
    normalize_uuid_16(0x2900),  # Characteristic Extended Properties
    normalize_uuid_16(0x2902),  # Client Characteristic Configuration
    normalize_uuid_16(0x2903),  # Server Characteristic Configuration
)
_DESCRIPTOR_TYPE_NSSTRING = (
    normalize_uuid_16(0x2901),  # Characteristic User Description
)
_DESCRIPTOR_NSNUMBER_SIZE = 2


def cb_uuid_to_str(uuid: CBUUIDType) -> str:
    """Converts a CoreBluetooth UUID to a Python string.

    If ``uuid`` is a 16-bit UUID, it is assumed to be a Bluetooth GATT UUID
    (``0000xxxx-0000-1000-8000-00805f9b34fb``).

    Args
        uuid: The UUID.

    Returns:
        The UUID as a lower case Python string (``xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx``)
    """
    return normalize_uuid_str(str(uuid.UUIDString()))


def to_optional_str(value: Any) -> Optional[str]:
    """Converts an NSString to a Python string, keeping ``None`` as ``None``."""
    return None if value is None else str(value)


def nsnumber_to_int(value: Any) -> int:
    """Converts an NSNumber returned through objc_util to a Python int."""
    return int(str(value))


def descriptor_value_to_bytearray(value: Any, descriptor_uuid: str) -> bytearray:
    """Converts a value of a CBDescriptor to the bytes sent by the peripheral."""
    if descriptor_uuid in _DESCRIPTOR_TYPE_NSNUMBER:
        return bytearray(
            nsnumber_to_int(value).to_bytes(_DESCRIPTOR_NSNUMBER_SIZE, "little")
        )
    if descriptor_uuid in _DESCRIPTOR_TYPE_NSSTRING:
        return bytearray(str(value).encode())
    return bytearray(nsdata_to_bytes(value))


def _is_uuid_16bit_compatible(_uuid: str) -> bool:
    test_uuid = "0000ffff-0000-1000-8000-00805f9b34fb"
    test_int = _convert_uuid_to_int(test_uuid)
    uuid_int = _convert_uuid_to_int(_uuid)
    result_int = uuid_int & test_int
    return uuid_int == result_int


def _convert_uuid_to_int(_uuid: str) -> int:
    UUID_cb = CBUUID.alloc().initWithString_(_uuid)
    UUID_data = UUID_cb.data()
    UUID_bytes = UUID_data.getBytes_length_(None, len(UUID_data))
    UUID_int = int.from_bytes(UUID_bytes, byteorder="big")
    return UUID_int


def _convert_int_to_uuid(i: int) -> str:
    UUID_bytes = i.to_bytes(length=16, byteorder="big")
    UUID_data = NSData.alloc().initWithBytes_length_(UUID_bytes, len(UUID_bytes))
    UUID_cb = CBUUID.alloc().initWithData_(UUID_data)
    return UUID_cb.UUIDString().lower()


def cb_uuid_to_uuid(uuid: CBUUIDType) -> UUID:
    return UUID(str(uuid.UUIDString()).replace("-", ""))
