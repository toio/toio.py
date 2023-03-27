# -*- coding: utf-8 -*-
# ************************************************************
#
#     battery.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pprint
from typing import Optional

from toio.cube.api.base_class import CubeCharacteristic, CubeResponse
from toio.device_interface import GattReadData
from toio.logger import get_toio_logger
from toio.toio_uuid import TOIO_UUID_BATTERY_INFO

logger = get_toio_logger(__name__)


class BatteryInformation(CubeResponse):
    """
    Cube remaining battery level response

    Attributes:
        battery_level (int): Battery level ( 0 <= battery_level <= 100)

    References:
        https://toio.github.io/toio-spec/en/docs/ble_battery#read-operations
    """

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return 0 <= payload[0] <= 100

    def __init__(self, payload: GattReadData):
        if BatteryInformation.is_myself(payload):
            self.battery_level = payload[0]
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


BatteryResponseType = BatteryInformation
"""
Response type of battery characteristic
"""


class Battery(CubeCharacteristic):
    """
    Battery characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_battery
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[BatteryResponseType]:
        if BatteryInformation.is_myself(payload):
            return BatteryInformation(payload)
        else:
            return None

    def __init__(self, interface):
        super().__init__(interface, TOIO_UUID_BATTERY_INFO)

    async def read(self) -> Optional[BatteryResponseType]:
        """
        Read the battery level

        Returns:
            BatteryInformation or None
            (None returns when read fails)

        References:
            https://toio.github.io/toio-spec/en/docs/ble_battery#read-operations
        """
        payload = await self._read()
        return self.is_my_data(payload)
