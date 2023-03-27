# -*- coding: utf-8 -*-
# ************************************************************
#
#     windows_ble.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

"""
Windows specific functions for ble scanner

"""

import re
import winreg
from typing import NamedTuple

from toio.logger import get_toio_logger

logger = get_toio_logger(__name__)

BLE_ENUM_KEY = R"SYSTEM\CurrentControlSet\Services\BthLEEnum\Enum"


def get_ble_device_address() -> tuple[str, ...]:
    device_prefix = "Dev_"
    ble_address: tuple = ()
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, BLE_ENUM_KEY)
    _subKeyNum, value_num, _modifiedDate = winreg.QueryInfoKey(key)
    for i in range(value_num):
        name, data, data_type = winreg.EnumValue(key, i)
        if data_type == winreg.REG_SZ:
            data = data.split("\\")
            if len(data) >= 2 and data[1].startswith(device_prefix):
                address = data[1][len(device_prefix) :]
                ble_address = ble_address + (address,)
                logger.debug("%s:%s:%s", name, address, data)
    return ble_address


class RegisteredCube(NamedTuple):
    name: str
    address: str


BLE_DEVICE_KEY = R"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices"


def get_registered_cubes() -> tuple[RegisteredCube, ...]:
    ble_address = get_ble_device_address()
    registered_cube: tuple = ()
    for address in ble_address:
        key_name = BLE_DEVICE_KEY + "\\" + str(address)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_name)
        _subKeyNum, value_num, _modifiedDate = winreg.QueryInfoKey(key)
        for i in range(value_num):
            name, data, _data_type = winreg.EnumValue(key, i)
            if name == "Name":
                if data[-1] == 0:
                    data = data[:-1]
                device_name = data.decode("utf-8")
                address_str = ":".join(re.split("(..)", address)[1::2]).upper()
                if device_name.startswith("toio Core Cube"):
                    registered_cube = registered_cube + (
                        RegisteredCube(device_name, address_str),
                    )
    return registered_cube
