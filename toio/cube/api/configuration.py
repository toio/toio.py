# -*- coding: utf-8 -*-
# ************************************************************
#
#     configuration.py
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
from toio.toio_uuid import TOIO_UUID_CONFIG
from toio.utility import clip

logger = get_toio_logger(__name__)


class RequestProtocolVersion(CubeCommand):
    """
    Protocol version request command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#requesting-the-ble-protocol-version
    """

    _payload_id = 0x01

    def __init__(self) -> None:
        pass

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00))


class SetHorizontalDetectionThreshold(CubeCommand):
    """
    Horizontal detection threshold setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#horizontal-detection-threshold-settings
    """

    _payload_id = 0x05

    def __init__(self, threshold: int) -> None:
        self.threshold = clip(threshold, 1, 45)

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.threshold))


class SetCollisionDetectionThreshold(CubeCommand):
    """
    Collision detection threshold setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#collision-detection-threshold-settings
    """

    _payload_id = 0x06

    def __init__(self, threshold: int) -> None:
        self.threshold = clip(threshold, 1, 10)

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.threshold))


class SetDoubleTapDetectionTimeInterval(CubeCommand):
    """
    Double-tap detection time interval setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#double-tap-detection-time-interval-settings
    """

    _payload_id = 0x17

    def __init__(self, threshold: int) -> None:
        self.threshold = clip(threshold, 1, 7)

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.threshold))


class NotificationCondition(IntEnum):
    """
    Notification conditions of ID notification

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#notification-conditions
    """

    Always = 0x00
    ChangeDetection = 0x01
    Periodic = 0xFF


class SetIdNotification(CubeCommand):
    """
    ID notification setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#identification-sensor-id-notification-settings
    """

    _payload_id = 0x18

    def __init__(self, interval_ms: int, condition: NotificationCondition) -> None:
        self.interval = clip(int(interval_ms / 10), 0, 255)
        self.condition = condition

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.interval, self.condition))


class SetIdMissedNotification(CubeCommand):
    """
    ID missed notification setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#identification-sensor-id-missed-notification-settings
    """

    _payload_id = 0x19

    def __init__(self, sensitivity_ms: int) -> None:
        self.sensitivity = clip(int(sensitivity_ms / 10), 0, 255)

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.sensitivity))


class MagneticSensorFunction(IntEnum):
    Disable = 0x00
    MagnetState = 0x01
    MagneticForce = 0x02


class MagneticSensorCondition(IntEnum):
    Always = 0x00
    ChangeDetection = 0x01


class SetMagneticSensor(CubeCommand):
    """
    Magnet sensor setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#magnetic-sensor-settings-
    """

    _payload_id = 0x1B

    def __init__(
        self,
        function_type: MagneticSensorFunction,
        interval_ms: int,
        condition: MagneticSensorCondition,
    ) -> None:
        self.function_type = function_type
        self.interval = clip(int(interval_ms / 20), 0, 255)
        self.condition = condition

    def __bytes__(self) -> bytes:
        return bytes(
            (self._payload_id, 0x00, self.function_type, self.interval, self.condition)
        )


class MotorSpeedInformationAcquisitionState(IntEnum):
    Disable = 0x00
    Enable = 0x01


class SetMotorSpeedInformationAcquisition(CubeCommand):
    """
    Motor speed information acquisition setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#motor-speed-information-acquisition-settings
    """

    _payload_id = 0x1C

    def __init__(self, state: MotorSpeedInformationAcquisitionState) -> None:
        self.state = state

    def __bytes__(self) -> bytes:
        return bytes((self._payload_id, 0x00, self.state))


class PostureAngleDetectionType(IntEnum):
    Euler = 0x01
    Quaternions = 0x02


class PostureAngleDetectionCondition(IntEnum):
    """
    Notification condition of posture angle detection

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#notification-conditions-1
    """

    Always = 0x00
    ChangeDetection = 0x01


class SetPostureAngleDetection(CubeCommand):
    """
    Posture angle detection setting command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#posture-angle-detection-settings-
    """

    _payload_id = 0x1D

    def __init__(
        self,
        detection_type: PostureAngleDetectionType,
        interval_ms: int,
        condition: PostureAngleDetectionCondition,
    ):
        self.detection_type = detection_type
        self.interval = clip(int(interval_ms / 10), 0, 255)
        self.condition = condition

    def __bytes__(self) -> bytes:
        return bytes(
            (self._payload_id, 0x00, self.detection_type, self.interval, self.condition)
        )


class ProtocolVersion(CubeResponse):
    """
    Protocol version response

    Attributes:
        version (str): version (UTF-8)

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#obtaining-the-ble-protocol-version
    """

    _payload_id = 0x81

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ProtocolVersion._payload_id

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            version = payload[2:]
            self.version = version.decode("UTF-8")
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseIdNotificationSettings(CubeResponse):
    """
    ID notification setting response

    Attributes:
        result (bool): Result of the command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#responses-to-identification-sensor-id-notification-settings
    """

    _payload_id = 0x98
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseIdNotificationSettings._payload_id

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            _, _, result = self._converter.unpack_from(payload)
            self.result = result == 0x00
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseIdMissedNotificationSettings(CubeResponse):
    """
    ID missed notification setting response

    Attributes:
        result (bool): Result of the command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#responses-to-identification-sensor-id-missed-notification-settings
    """

    _payload_id = 0x99
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseIdMissedNotificationSettings._payload_id

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            _, _, result = self._converter.unpack_from(payload)
            self.result = result == 0x00
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseMagneticSensorSettings(CubeResponse):
    """
    Magnetic sensor setting response

    Attributes:
        result (bool): Result of the command

    References:
       https://toio.github.io/toio-spec/en/docs/ble_configuration#responses-to-magnetic-sensor-settings
    """

    _payload_id = 0x9B
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseMagneticSensorSettings._payload_id

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            _, _, result = self._converter.unpack_from(payload)
            self.result = result == 0x00
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseMotorSpeedInformationAcquisitionSettings(CubeResponse):
    """
    Motor speed information setting response

    Attributes:
        result (bool): Result of the command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#responses-to-motor-speed-information-acquisition-settings
    """

    _payload_id = 0x9B
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return (
            payload[0] == ResponseMotorSpeedInformationAcquisitionSettings._payload_id
        )

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            _, _, result = self._converter.unpack_from(payload)
            self.result = result == 0x00
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponsePostureAngleDetectionSettings(CubeResponse):
    """
    Posture angle detection setting response

    Attributes:
        result (bool): Result of the command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration#responses-to-posture-angle-detection-settings-
    """

    _payload_id = 0x9B
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponsePostureAngleDetectionSettings._payload_id

    def __init__(self, payload: GattReadData):
        if ProtocolVersion.is_myself(payload):
            _, _, result = self._converter.unpack_from(payload)
            self.result = result == 0x00
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


ConfigurationResponseType: TypeAlias = Union[
    ProtocolVersion,
    ResponseIdNotificationSettings,
    ResponseIdMissedNotificationSettings,
    ResponseMagneticSensorSettings,
    ResponseMotorSpeedInformationAcquisitionSettings,
    ResponsePostureAngleDetectionSettings,
]
"""
Response types of configuration characteristic
"""


class Configuration(CubeCharacteristic):
    """
    Configuration characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_configuration
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[ConfigurationResponseType]:
        if ProtocolVersion.is_myself(payload):
            return ProtocolVersion(payload)
        elif ResponseIdNotificationSettings.is_myself(payload):
            return ResponseIdNotificationSettings(payload)
        elif ResponseIdMissedNotificationSettings.is_myself(payload):
            return ResponseIdNotificationSettings(payload)
        elif ResponseMagneticSensorSettings.is_myself(payload):
            return ResponseMagneticSensorSettings(payload)
        elif ResponseMotorSpeedInformationAcquisitionSettings.is_myself(payload):
            return ResponseMotorSpeedInformationAcquisitionSettings(payload)
        elif ResponsePostureAngleDetectionSettings.is_myself(payload):
            return ResponsePostureAngleDetectionSettings(payload)
        else:
            return None

    def __init__(self, interface: CubeInterface) -> None:
        self.interface = interface
        super().__init__(interface, TOIO_UUID_CONFIG)

    async def request_protocol_version(self) -> None:
        """
        Send protocol version request command

        This function DO NOT return response payload.
        Receive the result by notification.

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#requesting-the-ble-protocol-version
        """
        command = RequestProtocolVersion()
        await self._write(bytes(command))

    async def set_horizontal_detection_threshold(self, threshold: int) -> None:
        """
        Send horizontal detection threshold setting command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            threshold (int): Threshold

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#horizontal-detection-threshold-settings
        """
        command = SetHorizontalDetectionThreshold(threshold)
        await self._write(bytes(command))

    async def set_collision_detection_threshold(self, threshold: int) -> None:
        """
        Send collision detection threshold setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            threshold (int): Threshold

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#collision-detection-threshold-settings
        """
        command = SetHorizontalDetectionThreshold(threshold)
        await self._write(bytes(command))

    async def set_double_tap_detection_threshold(self, threshold: int) -> None:
        """
        Send double-tap detection threshold setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            threshold (int): Threshold

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#double-tap-detection-time-interval-settings
        """
        command = SetDoubleTapDetectionTimeInterval(threshold)
        await self._write(bytes(command))

    async def set_id_notification(
        self, interval_ms: int, condition: NotificationCondition
    ) -> None:
        """
        Send id information notification setting request command

        This function DO NOT return response payload.
        Receive the result by notification.


        Args:
            interval_ms (int): Notification interval [ms]
            condition (NotificationCondition): Condition

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#identification-sensor-id-notification-settings
        """
        command = SetIdNotification(interval_ms, condition)
        await self._write(bytes(command))

    async def set_id_missed_notification(self, sensitivity_ms: int) -> None:
        """
        Send ID missed notification setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            sensitivity_ms (int): Sensitivity [ms]

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#identification-sensor-id-missed-notification-settings
        """
        command = SetIdMissedNotification(sensitivity_ms)
        await self._write(bytes(command))

    async def set_magnetic_sensor(
        self,
        function_type: MagneticSensorFunction,
        interval_ms: int,
        condition: MagneticSensorCondition,
    ) -> None:
        """
        Send magnetic sensor setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            function_type (MagneticSensorFunction): Function type
            interval_ms (int): Notification interval [ms]
            condition (MagneticSensorCondition): Condition

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#magnetic-sensor-settings-
        """
        command = SetMagneticSensor(function_type, interval_ms, condition)
        await self._write(bytes(command))

    async def set_motor_speed_information_acquisition(
        self, state: MotorSpeedInformationAcquisitionState
    ) -> None:
        """
        Send motor speed information acquisition setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            state (MotorSpeedInformationAcquisitionState): state

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#motor-speed-information-acquisition-settings
        """
        command = SetMotorSpeedInformationAcquisition(state)
        await self._write(bytes(command))

    async def set_posture_angle_detection(
        self,
        detection_type: PostureAngleDetectionType,
        interval_ms: int,
        condition: PostureAngleDetectionCondition,
    ) -> None:
        """
        Send posture angle setting request command

        This function DO NOT return response payload.
        Receive the result by notification.

        Args:
            detection_type (PostureAngleDetectionType): Detection type
            interval_ms (int): Notification interval [ms]
            condition (PostureAngleDetectionCondition): Condition

        References:
            https://toio.github.io/toio-spec/en/docs/ble_configuration#posture-angle-detection-settings-
        """
        command = SetPostureAngleDetection(detection_type, interval_ms, condition)
        await self._write(bytes(command))
