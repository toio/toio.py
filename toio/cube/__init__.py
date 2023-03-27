# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/cube/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************


from typing import Optional
from uuid import UUID

from ..device_interface import GattNotificationHandler, GattReadData, GattWriteData
from .api import ToioCoreCubeLowLevelAPI
from .api.base_class import CubeInterface
from .api.battery import Battery, BatteryInformation, BatteryResponseType
from .api.button import Button, ButtonInformation, ButtonResponseType, ButtonState
from .api.configuration import (
    Configuration,
    ConfigurationResponseType,
    MagneticSensorCondition,
    MagneticSensorFunction,
    MotorSpeedInformationAcquisitionState,
    NotificationCondition,
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    ProtocolVersion,
    ResponseIdMissedNotificationSettings,
    ResponseIdNotificationSettings,
    ResponseMagneticSensorSettings,
    ResponseMotorSpeedInformationAcquisitionSettings,
    ResponsePostureAngleDetectionSettings,
)
from .api.id_information import (
    IdInformation,
    IdInformationResponseType,
    PositionId,
    PositionIdMissed,
    StandardId,
    StandardIdMissed,
)
from .api.indicator import Color, Indicator, IndicatorParam
from .api.motor import (
    AccelerationDirection,
    AccelerationPriority,
    AccelerationRotation,
    Motor,
    MotorResponseCode,
    MotorResponseType,
    MovementType,
    ResponseMotorControlMultipleTargets,
    ResponseMotorControlTarget,
    ResponseMotorSpeed,
    RotationOption,
    Speed,
    SpeedChangeType,
    TargetPosition,
    WriteMode,
)
from .api.sensor import (
    MagneticSensorData,
    MotionDetectionData,
    Posture,
    PostureAngleEulerData,
    PostureAngleQuaternionsData,
    PostureDataType,
    Sensor,
    SensorResponseType,
)
from .api.sound import MidiNote, Note, Sound, SoundId


class ToioCoreCube(CubeInterface):
    """
    Access to toio Core Cube

    Attributes:
        interface (CubeInterface): control interface (e.g. BleCube)
        name (str): cube name (optional)
        api (ToioCoreCubeLowLevelAPI): API class
    """

    def __init__(self, interface: CubeInterface, name: Optional[str] = None):
        self.interface = interface
        self.name = name
        self.api = ToioCoreCubeLowLevelAPI(interface)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self) -> bool:
        return await self.interface.connect()

    async def disconnect(self) -> bool:
        return await self.interface.disconnect()

    async def read(self, uuid: UUID) -> GattReadData:
        return await self.interface.read(uuid)

    async def write(self, uuid: UUID, data: GattWriteData, response: bool = False):
        return await self.interface.write(uuid, data, response)

    async def register_notification_handler(
        self, uuid: UUID, handler: GattNotificationHandler
    ) -> bool:
        return await self.interface.register_notification_handler(uuid, handler)

    async def unregister_notification_handler(self, uuid: UUID) -> bool:
        return await self.interface.unregister_notification_handler(uuid)


__all__: tuple[str, ...] = (
    "ToioCoreCube",
    # .api
    "ToioCoreCubeLowLevelAPI",
    # .api.battery
    "BatteryResponseType",
    "BatteryInformation",
    "Battery",
    # .api.button
    "ButtonResponseType",
    "ButtonState",
    "ButtonInformation",
    "Button",
    # .api.configuration
    "ConfigurationResponseType",
    "NotificationCondition",
    "MagneticSensorFunction",
    "MagneticSensorCondition",
    "MotorSpeedInformationAcquisitionState",
    "PostureAngleDetectionType",
    "PostureAngleDetectionCondition",
    "ProtocolVersion",
    "ResponseIdNotificationSettings",
    "ResponseIdMissedNotificationSettings",
    "ResponseMagneticSensorSettings",
    "ResponseMotorSpeedInformationAcquisitionSettings",
    "ResponsePostureAngleDetectionSettings",
    "Configuration",
    # .api.id_information
    "IdInformationResponseType",
    "PositionId",
    "StandardId",
    "PositionIdMissed",
    "StandardIdMissed",
    "IdInformation",
    # .api.indicator
    "Color",
    "IndicatorParam",
    "Indicator",
    # .api.motor
    "MotorResponseType",
    "MovementType",
    "RotationOption",
    "TargetPosition",
    "SpeedChangeType",
    "Speed",
    "WriteMode",
    "AccelerationRotation",
    "AccelerationDirection",
    "AccelerationPriority",
    "MotorResponseCode",
    "ResponseMotorControlTarget",
    "ResponseMotorControlMultipleTargets",
    "ResponseMotorSpeed",
    "Motor",
    # .api.sensor
    "SensorResponseType",
    "PostureDataType",
    "Posture",
    "MotionDetectionData",
    "PostureAngleEulerData",
    "PostureAngleQuaternionsData",
    "MagneticSensorData",
    "Sensor",
    # .api.sound
    "SoundId",
    "Note",
    "MidiNote",
    "Sound",
)
