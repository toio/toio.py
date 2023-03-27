# -*- coding: utf-8 -*-
# ************************************************************
#
#     sensor.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pprint
import struct
from enum import IntEnum
from typing import Optional, TypeAlias, Union

from toio.cube.api.base_class import CubeCharacteristic, CubeCommand, CubeResponse
from toio.device_interface import CubeInterface, GattReadData
from toio.logger import get_toio_logger
from toio.toio_uuid import TOIO_UUID_SENSOR_INFO

logger = get_toio_logger(__name__)


class RequestMotionDetection(CubeCommand):
    """
    Motion information request command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sensor#requesting-motion-detection-information
    """

    _payload_id = 0x81

    def __init__(self):
        pass

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id,))


class PostureDataType(IntEnum):
    Euler = 0x01
    Quaternions = 0x02


class RequestPostureAngleDetection(CubeCommand):
    """
    Posture angle information request command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_high_precision_tilt_sensor#requesting-posture-angle-detection
    """

    _payload_id = 0x83

    def __init__(self, data_type: PostureDataType):
        self.data_type = data_type

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, self.data_type))


class RequestMagneticSensor(CubeCommand):
    """
    Magnetic sensor information request command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_magnetic_sensor#requests-for-magnetic-sensor-information
    """

    _payload_id = 0x82

    def __init__(self):
        pass

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id,))


class Posture(IntEnum):
    """Posture
    Orientation of the cube.

    Reference:
        https://toio.github.io/toio-spec/en/docs/ble_sensor/#posture-detection
    """

    Unknown = 0
    Top = 1
    Bottom = 2
    Rear = 3
    Front = 4
    Right = 5
    Left = 6


class MotionDetectionData(CubeResponse):
    """MotionDetectionData
    Information on the cube's motion detection.

    Attributes:
        horizontal (bool): Horizontal detection
        collision (bool): Collision detection
        double_tap (bool): Double-tap detection
        posture (Posture): Posture detection
        shake (int): Shake detection (0:no shake, 1:Level1 - 10:Level10)

    Reference:
        https://toio.github.io/toio-spec/en/docs/ble_sensor/#obtaining-motion-detection-information
    """

    _payload_id = 0x01
    _converter = struct.Struct("<BBBBBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == MotionDetectionData._payload_id

    def __init__(self, payload: GattReadData):
        if MotionDetectionData.is_myself(payload):
            (
                _,
                horizontal,
                collision,
                double_tap,
                posture,
                shake,
            ) = self._converter.unpack_from(payload)
            self.horizontal = horizontal != 0
            self.collision = collision != 0
            self.double_tap = double_tap != 0
            self.posture = Posture(posture)
            self.shake = shake
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class PostureAngleEulerData(CubeResponse):
    """PostureAngleEulerData

    Information of posture angle (Euler angle)

    Attributes:
        roll (int): Roll (X axis)
        pitch (int): Pitch (Y axis)
        yaw (nt): Yaw (Z axis)

    References:
       https://toio.github.io/toio-spec/en/docs/ble_high_precision_tilt_sensor#obtaining-posture-angle-information-notifications-in-euler-angles

    """

    _payload_id = 0x03
    _converter = struct.Struct("<BBhhh")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return (
            payload[0] == PostureAngleEulerData._payload_id
            and payload[1] == PostureDataType.Euler
        )

    def __init__(self, payload: GattReadData):
        if PostureAngleEulerData.is_myself(payload):
            _, _, self.roll, self.pitch, self.yaw = self._converter.unpack_from(payload)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class PostureAngleQuaternionsData(CubeResponse):
    """PostureAngleQuaternionData

    Information of posture angle (Quaternion)

    Attributes:
        w (int):
        x (int):
        y (int):
        z (int):

    References:
        https://toio.github.io/toio-spec/en/docs/ble_high_precision_tilt_sensor#obtaining-posture-angle-information-notifications-in-quaternions
    """

    _payload_id = 0x03
    _converter = struct.Struct("<BBhhhh")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return (
            payload[0] == PostureAngleQuaternionsData._payload_id
            and payload[1] == PostureDataType.Quaternions
        )

    def __init__(self, payload: GattReadData):
        if PostureAngleQuaternionsData.is_myself(payload):
            _, _, self.w, self.x, self.y, self.z = self._converter.unpack_from(payload)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class MagneticSensorData(CubeResponse):
    """MagneticSensorData

    Information of magnetic sensor

    Attributes:
        state (int): Magnet state
        strength (int): Magnetic force strength
        x (int): Magnetic force direction (X axis)
        y (int): Magnetic force direction (Y axis)
        z (int): Magnetic force direction (Z axis)

    References:
        https://toio.github.io/toio-spec/en/docs/ble_magnetic_sensor/#obtaining-magnetic-sensor-information-
    """

    _payload_id = 0x02
    _converter = struct.Struct("<BBBbbb")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == MagneticSensorData._payload_id

    def __init__(self, payload: GattReadData):
        if MagneticSensorData.is_myself(payload):
            (
                _,
                self.state,
                self.strength,
                self.x,
                self.y,
                self.z,
            ) = self._converter.unpack_from(payload)
        else:
            raise TypeError("wrong payload")


SensorResponseType: TypeAlias = Union[
    MotionDetectionData,
    PostureAngleEulerData,
    PostureAngleQuaternionsData,
    MagneticSensorData,
]
"""
Response types of Sensor characteristic
"""


class Sensor(CubeCharacteristic):
    """
    Sensor information characteristic

    References:
        `Motion detection <https://toio.github.io/toio-spec/en/docs/ble_sensor>`_

        `Posture angle detection <https://toio.github.io/toio-spec/en/docs/ble_high_precision_tilt_sensor>`_

        `Magnetic sensor <https://toio.github.io/toio-spec/en/docs/ble_magnetic_sensor>`_
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[SensorResponseType]:
        if MotionDetectionData.is_myself(payload):
            return MotionDetectionData(payload)
        elif PostureAngleEulerData.is_myself(payload):
            return PostureAngleEulerData(payload)
        elif PostureAngleQuaternionsData.is_myself(payload):
            return PostureAngleQuaternionsData(payload)
        elif MagneticSensorData.is_myself(payload):
            return MagneticSensorData(payload)
        else:
            return None

    def __init__(self, interface: CubeInterface):
        self.interface = interface
        super().__init__(interface, TOIO_UUID_SENSOR_INFO)

    async def read(self) -> Optional[SensorResponseType]:
        """
        Read sensor information response

        Returns:
            One of SensorInformationData or None
            (None returns when read fails)
        """
        payload = await self._read()
        return self.is_my_data(payload)

    async def request_motion_information(self) -> None:
        """
        Send motion information request command
        """
        request = RequestMotionDetection()
        await self._write(bytes(request))

    async def request_posture_angle_information(
        self, data_type: PostureDataType
    ) -> None:
        """
        Send posture angle information request command
        """
        request = RequestPostureAngleDetection(data_type)
        await self._write(bytes(request))

    async def request_magnetic_sensor_information(self) -> None:
        """
        Send magnetic sensor information request
        """
        request = RequestMagneticSensor()
        await self._write(bytes(request))
