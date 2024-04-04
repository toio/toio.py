# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio_uuid.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import uuid
from enum import Enum

TOIO_UUID_SERVICE = uuid.UUID("10B20100-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_ID_INFO = uuid.UUID("10B20101-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_SENSOR_INFO = uuid.UUID("10B20106-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_BUTTON_INFO = uuid.UUID("10B20107-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_BATTERY_INFO = uuid.UUID("10B20108-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_MOTOR_CTRL = uuid.UUID("10B20102-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_LIGHT_CTRL = uuid.UUID("10B20103-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_SOUND_CTRL = uuid.UUID("10B20104-5B3B-4571-9508-CF3EFCD7BBAE")
TOIO_UUID_CONFIG = uuid.UUID("10B201FF-5B3B-4571-9508-CF3EFCD7BBAE")


class ToioUuid(Enum):
    Service = TOIO_UUID_SERVICE
    Id = TOIO_UUID_ID_INFO
    Sensor = TOIO_UUID_SENSOR_INFO
    Button = TOIO_UUID_BUTTON_INFO
    Battery = TOIO_UUID_BATTERY_INFO
    Motor = TOIO_UUID_MOTOR_CTRL
    Light = TOIO_UUID_LIGHT_CTRL
    Sound = TOIO_UUID_SOUND_CTRL
    Config = TOIO_UUID_CONFIG
