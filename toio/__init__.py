# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from .coordinate_systems import (
    ToioRelativeCoordinateSystem,
    VisualProgrammingCoordinateSystem,
)
from .cube import ToioCoreCube
from .cube.api import ToioCoreCubeLowLevelAPI
from .cube.api.battery import Battery, BatteryInformation, BatteryResponseType
from .cube.api.button import Button, ButtonInformation, ButtonResponseType, ButtonState
from .cube.api.configuration import (
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
from .cube.api.id_information import (
    IdInformation,
    IdInformationResponseType,
    PositionId,
    PositionIdMissed,
    StandardId,
    StandardIdMissed,
)
from .cube.api.indicator import Color, Indicator, IndicatorParam
from .cube.api.motor import (
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
from .cube.api.sensor import (
    MagneticSensorData,
    MotionDetectionData,
    Posture,
    PostureAngleEulerData,
    PostureAngleQuaternionsData,
    PostureDataType,
    Sensor,
    SensorResponseType,
)
from .cube.api.sound import MidiNote, Note, Sound, SoundId
from .position import (
    CoordinateSystemABC,
    CubeLocation,
    DefaultCoordinateSystem,
    MatRect,
    Point,
    RelativeCubeLocation,
    ToioMat,
)
from .scanner import BLEScanner

__all__ = [
    # .coordinate_system
    "ToioRelativeCoordinateSystem",
    "VisualProgrammingCoordinateSystem",
    # .cube
    "ToioCoreCube",
    # .cube.api
    "ToioCoreCubeLowLevelAPI",
    # .cube.api.battery
    "BatteryResponseType",
    "BatteryInformation",
    "Battery",
    # .cube.api.button
    "ButtonResponseType",
    "ButtonState",
    "ButtonInformation",
    "Button",
    # .cube.api.configuration
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
    # .cube.api.id_information
    "IdInformationResponseType",
    "PositionId",
    "StandardId",
    "PositionIdMissed",
    "StandardIdMissed",
    "IdInformation",
    # .cube.api.indicator
    "Color",
    "IndicatorParam",
    "Indicator",
    # .cube.api.motor
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
    # .cube.api.sensor
    "SensorResponseType",
    "PostureDataType",
    "Posture",
    "MotionDetectionData",
    "PostureAngleEulerData",
    "PostureAngleQuaternionsData",
    "MagneticSensorData",
    "Sensor",
    # .cube.api.sound
    "SoundId",
    "Note",
    "MidiNote",
    "Sound",
    # .position
    "Point",
    "CubeLocation",
    "MatRect",
    "CoordinateSystemABC",
    "DefaultCoordinateSystem",
    "RelativeCubeLocation",
    "ToioMat",
    # .scanner
    "BLEScanner",
]
