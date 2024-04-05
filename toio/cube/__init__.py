# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/cube/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import collections
from uuid import UUID

from typing_extensions import (
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeAlias,
    Union,
)

from ..device_interface import (
    CubeInfo,
    CubeInterface,
    GattNotificationHandler,
    GattReadData,
    GattWriteData,
)
from .api import ToioCoreCubeLowLevelAPI
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
from .multi_cubes import MultipleToioCoreCubes
from .notification_handler_info import NotificationHandlerInfo, NotificationHandlerTypes

CubeInitializer: TypeAlias = Union[CubeInterface, CubeInfo]


class ToioCoreCube(CubeInterface):
    """
    Access to toio Core Cube

    Note:
       self.protocol_version is set after connecting to the cube.
       self.protocol_version and self.max_retry_to_get_protocol_version is supported since v1.2.0.

       In the next version, ToioCoreCube class will no longer have CubeInterface as an abstract base class.

    Attributes:
        interface (CubeInterface): control interface (e.g. BleCube)
        name (str): cube name (optional)
        api (ToioCoreCubeLowLevelAPI): API class
        protocol_version (Optional[ProtocolVersion]): protocol version of the cube
        max_retry_to_get_protocol_version (int): number of retries to get protocol version

    """

    SUPPORTED_MAJOR_VERSION: int = 2
    SUPPORTED_MINOR_VERSION: int = 4

    @staticmethod
    def create(
        initializer: Union[CubeInitializer, collections.Sequence]
    ) -> ToioCoreCube:
        """
        Supported toio.py versions: v1.2.0 or later

        Create a ToioCoreCube instance from a CubeInterface or CubeInfo

        Args:
            initializer (CubeInitializer): initializer

        Returns:
            Optional[ToioCoreCube]:
        """
        if (
            isinstance(initializer, Sequence)
            and not isinstance(initializer, CubeInterface)
            and not isinstance(initializer, CubeInfo)
        ):
            if len(initializer) < 1:
                raise ValueError("no initializer")
            first_initializer = initializer[0]
        else:
            first_initializer = initializer

        if isinstance(first_initializer, CubeInterface):
            return ToioCoreCube(interface=first_initializer)
        elif isinstance(first_initializer, CubeInfo):
            return ToioCoreCube(
                interface=first_initializer.interface, name=first_initializer.name
            )
        else:
            raise ValueError("wrong initializer: " + str(type(first_initializer)))

    @staticmethod
    def create_cubes(initializers: Iterable[CubeInitializer]) -> List[ToioCoreCube]:
        """
        Supported toio.py versions: v1.2.0 or later

        Create a ToioCoreCube instance list from a CubeInterface or CubeInfo list

        Args:
            initializers (Iterable[CubeInitializer]): initializers

        Returns:
            List[ToioCoreCube]:
        """
        cubes = []
        for initializer in initializers:
            cube = ToioCoreCube.create(initializer)
            cubes.append(cube)
        return cubes

    def __init__(self, interface: CubeInterface, name: Optional[str] = None):
        self.interface = interface
        self.name = name
        self.api = ToioCoreCubeLowLevelAPI(interface=interface, root_device=self)
        self.protocol_version: Optional[ProtocolVersion] = None
        self.max_retry_to_get_protocol_version: int = 10

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self) -> bool:
        connect_result = await self.interface.connect()
        if connect_result is True:
            self.protocol_version = None
            await self.api.configuration.request_protocol_version()
            retry_count = 0
            while (
                self.protocol_version is None
                and retry_count < self.max_retry_to_get_protocol_version
            ):
                retry_count += 1
                received_data = await self.api.configuration._read()
                if ProtocolVersion.is_myself(received_data):
                    self.protocol_version = ProtocolVersion(received_data)
                    import asyncio

                    await asyncio.sleep(0.1)
            if self.protocol_version is not None:
                if (
                    self.protocol_version._major != self.SUPPORTED_MAJOR_VERSION
                    or self.protocol_version._minor < self.SUPPORTED_MINOR_VERSION
                ):
                    import warnings

                    warnings.warn(
                        "protocol version %s is not supported by toio.py\n"
                        % self.protocol_version.version
                        + "update cube firmware to latest version",
                        UserWarning,
                    )
        return connect_result

    async def disconnect(self) -> bool:
        return await self.interface.disconnect()

    async def read(self, char_uuid: UUID) -> GattReadData:
        return await self.interface.read(char_uuid)

    async def write(self, char_uuid: UUID, data: GattWriteData, response: bool = False):
        return await self.interface.write(char_uuid, data, response)

    async def register_notification_handler(
        self, char_uuid: UUID, notification_handler: GattNotificationHandler
    ) -> bool:
        return await self.interface.register_notification_handler(
            char_uuid, notification_handler
        )

    async def unregister_notification_handler(self, char_uuid: UUID) -> bool:
        return await self.interface.unregister_notification_handler(char_uuid)

    def is_connect(self) -> bool:
        return self.interface.is_connect()


__all__: Tuple[str, ...] = (
    "CubeInitializer",
    "ToioCoreCube",
    "NotificationHandlerInfo",
    "NotificationHandlerTypes",
    "MultipleToioCoreCubes",
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
