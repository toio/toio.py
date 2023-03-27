# -*- coding: utf-8 -*-
# ************************************************************
#
#     indicator.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import struct
from dataclasses import dataclass
from typing import Union

from toio.cube.api.base_class import CubeCharacteristic, CubeCommand
from toio.device_interface import CubeInterface, GattReadData
from toio.logger import get_toio_logger
from toio.toio_uuid import TOIO_UUID_LIGHT_CTRL
from toio.utility import clip

logger = get_toio_logger(__name__)


@dataclass
class Color:
    """
    Indicator color in RGB
    """

    r: int
    """R value (0 - 255)"""
    g: int
    """G value (0 - 255)"""
    b: int
    """B value (0 - 255)"""

    def flatten(self):
        """
        Return the tuple representation of this dataclass
        """
        r = clip(self.r, 0, 255)
        g = clip(self.g, 0, 255)
        b = clip(self.b, 0, 255)
        return r, g, b


@dataclass
class IndicatorParam:
    """
    Indicator color and lighting period
    """

    duration_ms: int
    """
    | Duration of lighting:
    |     Any fraction less than 10ms will be truncated.
    |     0 - 9: no time limit
    |     10 - 2550: duration [ms]
    """
    color: Color
    """
    |    RGB value
    """

    def flatten(self):
        duration = clip(int(self.duration_ms / 10), 0, 255)
        return duration, 0x01, 0x01, *self.color.flatten()


class TurningOnAndOff(CubeCommand):
    """
    Indicator turning on / off command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_light#turning-the-indicator-on-and-off
    """

    _payload_id = 0x03
    _converter = struct.Struct("<BBBBBBB")

    def __init__(self, param: IndicatorParam):
        self.param = param

    def __bytes__(self) -> bytes:
        return self._converter.pack(self._payload_id, *self.param.flatten())


class RepeatedTurningOnAndOff(CubeCommand):
    """
    Repeated indicator turning on /off command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_light#repeated-turning-on-and-off-of-indicator
    """

    _payload_id = 0x04
    _converter = struct.Struct("<BBB")
    REPEAT_INFINITE = 0

    def __init__(
        self,
        repeat: int,
        param_list: Union[list[IndicatorParam], tuple[IndicatorParam, ...]],
    ) -> None:
        self.repeat = repeat
        self.param_list = param_list

    def __bytes__(self) -> bytes:
        byte_representation = self._converter.pack(
            self._payload_id, self.repeat, len(self.param_list)
        )
        for param in self.param_list:
            byte_representation = byte_representation + struct.pack(
                "<BBBBBB", *param.flatten()
            )
        return byte_representation


class TurnOffAll(CubeCommand):
    """
    Indicator all off command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_light#turn-off-all-indicators
    """

    _payload_id = 0x01

    def __init__(self) -> None:
        pass

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id,))


class TurnOff(CubeCommand):
    """
    Indicator off command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_light#turn-off-a-specific-indicator
    """

    _payload_id = 0x02
    _converter = struct.Struct("<BBB")

    def __init__(self, indicator_id: int) -> None:
        self.indicator_id = indicator_id

    def __bytes__(self) -> bytes:
        return self._converter.pack(self._payload_id, 0x01, self.indicator_id)


class Indicator(CubeCharacteristic):
    """
    Indicator characteristic

    References:
       https://toio.github.io/toio-spec/en/docs/ble_light
    """

    @staticmethod
    def is_my_data(_payload: GattReadData) -> None:
        return None

    def __init__(self, interface: CubeInterface):
        self.interface = interface
        super().__init__(interface, TOIO_UUID_LIGHT_CTRL)

    async def turn_on(self, param: IndicatorParam) -> None:
        """
        Send indicator turn on / off command

        Args:
            param: Indicator parameter

        References:
            https://toio.github.io/toio-spec/en/docs/ble_light#repeated-turning-on-and-off-of-indicator
        """
        turn_on = TurningOnAndOff(param)
        await self._write(bytes(turn_on))

    async def repeated_turn_on(
        self,
        repeat: int,
        param_list: Union[list[IndicatorParam], tuple[IndicatorParam, ...]],
    ) -> None:
        """
        Send repeated indicator turning on / off command

        Args:
            repeat (int): Number of repetitions
            param_list (Union[list[IndicatorParam], tuple[IndicatorParam]]): List of indicator parameters

        References:
            https://toio.github.io/toio-spec/en/docs/ble_light#repeated-turning-on-and-off-of-indicator
        """
        repeated = RepeatedTurningOnAndOff(repeat, param_list)
        await self._write(bytes(repeated))

    async def turn_off_all(self) -> None:
        """
        Send all off command

        References:
            https://toio.github.io/toio-spec/en/docs/ble_light#turn-off-all-indicators
        """
        turn_off = TurnOffAll()
        await self._write(bytes(turn_off))

    async def turn_off(self, indicator_id: int) -> None:
        """
        Send off command

        Args:
            indicator_id (int): Indicator ID

        References:
            https://toio.github.io/toio-spec/en/docs/ble_light#turn-off-a-specific-indicator
        """
        turn_off = TurnOff(indicator_id)
        await self._write(bytes(turn_off))
