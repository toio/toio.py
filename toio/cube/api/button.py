# -*- coding: utf-8 -*-
# ************************************************************
#
#     button.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pprint
from enum import IntEnum

from typing_extensions import Optional, TypeAlias

from ...device_interface import CubeInterface, GattReadData
from ...logger import get_toio_logger
from ...toio_uuid import ToioUuid
from ..api.base_class import CubeCharacteristic, CubeResponse
from ..notification_handler_info import NotificationReceivedDevice

logger = get_toio_logger(__name__)


class ButtonState(IntEnum):
    """
    Value of the state of cube button
    """

    RELEASED = 0x00
    PRESSED = 0x80


class ButtonInformation(CubeResponse):
    """
    Cube button state response

    Attributes:
        state (ButtonState): State of the cube button

    References:
        https://toio.github.io/toio-spec/en/docs/ble_button#read-operations
    """

    _payload_id = 0x01

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ButtonInformation._payload_id

    def __init__(self, payload: GattReadData):
        if ButtonInformation.is_myself(payload):
            self.state = ButtonState(payload[1])
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


ButtonResponseType: TypeAlias = ButtonInformation
"""
Response type of button characteristic
"""


class Button(CubeCharacteristic):
    """
    Button characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_button
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[ButtonResponseType]:
        if ButtonInformation.is_myself(payload):
            return ButtonInformation(payload)
        else:
            return None

    def __init__(self, interface: CubeInterface, device: NotificationReceivedDevice):
        self.interface = interface
        super().__init__(interface, ToioUuid.Button.value, device)

    async def read(self) -> Optional[ButtonResponseType]:
        """
        Read the state of button

        Returns:
            ButtonInformation or None
            (None returns when read fails)

        References:
            https://toio.github.io/toio-spec/en/docs/ble_button#read-operations
        """
        payload = await self._read()
        return self.is_my_data(payload)
