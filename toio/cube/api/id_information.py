# -*- coding: utf-8 -*-
# ************************************************************
#
#     id_information.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pprint
import struct
from typing import Optional, Union

from toio.cube.api.base_class import CubeCharacteristic, CubeResponse
from toio.device_interface import CubeInterface, GattReadData
from toio.position import CubeLocation, Point
from toio.toio_uuid import TOIO_UUID_ID_INFO


class PositionId(CubeResponse):
    """
    Position id information response

    References:
        https://toio.github.io/toio-spec/en/docs/ble_id#position-id
    """

    _payload_id = 0x01
    _converter = struct.Struct("<BHHHHHH")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == PositionId._payload_id

    def __init__(self, payload: GattReadData):
        if PositionId.is_myself(payload):
            _, cx, cy, ca, sx, sy, sa = self._converter.unpack_from(payload)
            self.center = CubeLocation(point=Point(cx, cy), angle=ca)
            self.sensor = CubeLocation(point=Point(sx, sy), angle=sa)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class StandardId(CubeResponse):
    """
    Standard id information response

    References:
        https://toio.github.io/toio-spec/en/docs/ble_id#standard-id
    """

    _payload_id = 0x02
    _converter = struct.Struct("<BLH")

    @staticmethod
    def is_myself(data: GattReadData) -> bool:
        return data[0] == StandardId._payload_id

    def __init__(self, payload: GattReadData):
        if StandardId.is_myself(payload):
            _, self.value, self.angle = self._converter.unpack_from(payload)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class PositionIdMissed(CubeResponse):
    """
    Position id missed response

    References:
        https://toio.github.io/toio-spec/en/docs/ble_id#position-id-missed
    """

    _payload_id = 0x03
    _converter = struct.Struct("<B")

    @staticmethod
    def is_myself(data: GattReadData) -> bool:
        return data[0] == PositionIdMissed._payload_id

    def __init__(self, payload: GattReadData):
        if PositionIdMissed.is_myself(payload):
            pass
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return "Position ID missed"


class StandardIdMissed(CubeResponse):
    """
    Standard id information response

    References:
        https://toio.github.io/toio-spec/en/docs/ble_id#standard-id-missed
    """

    _payload_id = 0x04
    _converter = struct.Struct("<B")

    @staticmethod
    def is_myself(data: GattReadData) -> bool:
        return data[0] == StandardIdMissed._payload_id

    def __init__(self, payload: GattReadData):
        if StandardIdMissed.is_myself(payload):
            pass
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return "Standard ID missed"


IdInformationResponseType = Union[
    PositionId, StandardId, PositionIdMissed, StandardIdMissed
]
"""
Response types of id information characteristic
"""


class IdInformation(CubeCharacteristic):
    """
    ID sensor characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_id
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[IdInformationResponseType]:
        if PositionId.is_myself(payload):
            return PositionId(payload)
        elif StandardId.is_myself(payload):
            return StandardId(payload)
        elif PositionIdMissed.is_myself(payload):
            return PositionIdMissed(payload)
        elif StandardIdMissed.is_myself(payload):
            return StandardIdMissed(payload)
        else:
            return None

    def __init__(self, interface: CubeInterface):
        self.interface = interface
        super().__init__(interface, TOIO_UUID_ID_INFO)

    async def read(self) -> Optional[IdInformationResponseType]:
        """
        Read id information response

        Returns:
            One of IdInformationData or None
            (None returns when read fails)
        """
        payload = await self._read()
        return self.is_my_data(payload)
