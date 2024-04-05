# -*- coding: utf-8 -*-
# ************************************************************
#
#     battery.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import pprint

from typing_extensions import Optional

from ...device_interface import CubeInterface, GattReadData
from ...logger import get_toio_logger
from ...toio_uuid import ToioUuid
from ..api.base_class import CubeCharacteristic, CubeResponse
from ..notification_handler_info import NotificationReceivedDevice

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

    def __init__(self, interface: CubeInterface, device: NotificationReceivedDevice):
        super().__init__(interface, ToioUuid.Battery.value, device)

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
