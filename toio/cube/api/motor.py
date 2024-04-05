# -*- coding: utf-8 -*-
# ************************************************************
#
#     motor.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import pprint
import struct
from dataclasses import dataclass
from enum import Enum, IntEnum

from typing_extensions import List, Optional, Sequence, TypeAlias, Union

from ...device_interface import CubeInterface, GattReadData
from ...logger import get_toio_logger
from ...position import CubeLocation, Point
from ...toio_uuid import ToioUuid
from ...utility import clip
from ..api.base_class import CubeCharacteristic, CubeCommand, CubeResponse
from ..notification_handler_info import NotificationReceivedDevice

logger = get_toio_logger(__name__)


class MotorControl(CubeCommand):
    """
    Motor control command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control
    """

    _payload_id_motor_control = 0x01
    _payload_id_motor_control_with_duration = 0x02

    def __init__(self, left: int, right: int, duration_ms: Optional[int]):
        self.left = left
        self.right = right
        if duration_ms is not None:
            self.duration = clip(int(duration_ms / 10), 0, 255)
        else:
            self.duration = None

    @staticmethod
    def speed_to_param(speed):
        if speed >= 0:
            direction = 0x01
            value = min(speed, 255)
        else:
            direction = 0x02
            value = min(-speed, 255)
        return direction, value

    def __bytes__(self) -> bytes:
        l_dir, l_val = self.speed_to_param(self.left)
        r_dir, r_val = self.speed_to_param(self.right)
        if self.duration is None:
            return struct.pack(
                "<BBBBBBB",
                self._payload_id_motor_control,
                0x01,
                l_dir,
                l_val,
                0x02,
                r_dir,
                r_val,
            )
        else:
            return struct.pack(
                "<BBBBBBBB",
                self._payload_id_motor_control_with_duration,
                0x01,
                l_dir,
                l_val,
                0x02,
                r_dir,
                r_val,
                self.duration,
            )

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class MovementType(IntEnum):
    """
    Movement type

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#movement-type
    """

    Curve = 0
    CurveWithoutReverse = 1
    Linear = 2


class RotationOption(IntEnum):
    """
    Rotation Option

    Angle of the cube at the target point

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#%CE%B8-angle-of-the-cube-at-the-target-point
    """

    AbsoluteOptimal = 0
    AbsolutePositive = 1
    AbsoluteNegative = 2
    RelativePositive = 3
    RelativeNegative = 4
    WithoutRotation = 5
    SameAsAtWriting = 6


@dataclass
class TargetPosition:
    """
    Target position parameter
    """

    cube_location: CubeLocation
    """
    Target position of the cube
    """
    rotation_option: RotationOption = RotationOption.AbsoluteOptimal
    """
    Rotation option
    """

    @staticmethod
    def from_int(
        x: int = 0,
        y: int = 0,
        angle: int = 0,
        rotation_option: int = int(RotationOption.AbsoluteOptimal),
    ) -> TargetPosition:
        return TargetPosition(
            cube_location=CubeLocation(point=Point(x, y), angle=angle),
            rotation_option=RotationOption(rotation_option),
        )

    def flatten(self):
        return (
            self.cube_location.point.x,
            self.cube_location.point.y,
            (self.cube_location.angle & 0x0FFF) | ((self.rotation_option & 0xF) << 13),
        )


class SpeedChangeType(IntEnum):
    """
    Speed change type

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#motor-speed-change-types
    """

    Constant = 0
    Acceleration = 1
    Deceleration = 2
    AccelerationAndDeceleration = 3


@dataclass
class Speed:
    """
    Speed parameter
    """

    max: int = 0
    """
    Max speed
    """
    speed_change_type: SpeedChangeType = SpeedChangeType.Constant
    """
    Speed change type
    """

    @staticmethod
    def from_int(
        max: int = 0, speed_change_type: int = int(SpeedChangeType.Constant)
    ) -> Speed:
        return Speed(max=max, speed_change_type=SpeedChangeType(speed_change_type))

    def flatten(self):
        return self.max, int(self.speed_change_type)


class MotorControlTarget(CubeCommand):
    """
    Target specified motor control command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control-with-target-specified
    """

    _payload_id = 0x03
    _converter = struct.Struct("<BBBBBBBHHH")

    def __init__(
        self,
        timeout: int,
        movement_type: MovementType,
        speed: Speed,
        target: TargetPosition,
    ):
        self.timeout = clip(timeout, 0, 255)
        self.movement_type = movement_type
        self.speed = speed
        self.target = target

    def __bytes__(self) -> bytes:
        return self._converter.pack(
            self._payload_id,
            0x00,
            self.timeout,
            self.movement_type,
            *self.speed.flatten(),
            0x00,
            *self.target.flatten(),
        )

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class WriteMode(IntEnum):
    """
    Write mode of MotorControlMultipleTargets()

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#additional-write-operation-settings
    """

    Overwrite = 0
    Append = 1


class MotorControlMultipleTargets(CubeCommand):
    """
    Multiple targets specified motor control command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control-with-multiple-targets-specified
    """

    _payload_id = 0x04
    _converter = struct.Struct("<BBBBBBBB")

    def __init__(
        self,
        timeout: int,
        movement_type: MovementType,
        speed: Speed,
        mode: WriteMode,
        target_list: Sequence[TargetPosition],
    ):
        self.timeout = clip(timeout, 0, 255)
        self.movement_type = movement_type
        self.speed = speed
        self.mode = mode
        self.target_list = target_list

    def __bytes__(self) -> bytes:
        header = self._converter.pack(
            self._payload_id,
            0x00,
            self.timeout,
            self.movement_type,
            *self.speed.flatten(),
            0x00,
            int(self.mode),
        )
        body = bytes()
        for target in self.target_list:
            body = body + struct.pack("<HHH", *target.flatten())
        return header + body

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class AccelerationRotation(IntEnum):
    """
    Rotational direction when the cube is changing orientation

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor/#rotational-direction-when-cube-changes-orientation
    """

    Positive = 0
    Negative = 1


class AccelerationDirection(IntEnum):
    """
    Direction of cube travel

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor/#direction-of-cube-travel
    """

    Forward = 0
    Backward = 1


class AccelerationPriority(IntEnum):
    """
    Priority to the translational speed or the rotational velocity

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor/#priority-designation
    """

    TranslationalVelocity = 0
    RotationalVelocity = 1


class MotorControlAcceleration(CubeCommand):
    """
    Acceleration specified motor control command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor/#motor-control-with-acceleration-specified
    """

    _payload_id = 0x05
    _converter = struct.Struct("<BBBHBBBB")

    def __init__(
        self,
        translation: int,
        acceleration: int,
        rotation_velocity: int,
        rotation_direction: AccelerationRotation,
        cube_direction: AccelerationDirection,
        priority: AccelerationPriority,
        duration_ms: int,
    ):
        self.translation = clip(translation, 0, 255)
        self.acceleration = clip(acceleration, 0, 255)
        self.rotation_velocity = clip(rotation_velocity, 0, 0xFFFF)
        self.rotation_direction = rotation_direction
        self.cube_direction = cube_direction
        self.priority = priority
        self.duration = clip(int(duration_ms / 10), 0, 255)

    def __bytes__(self) -> bytes:
        return self._converter.pack(
            self._payload_id,
            self.translation,
            self.acceleration,
            self.rotation_velocity,
            self.rotation_direction,
            self.cube_direction,
            self.priority,
            self.duration,
        )

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class MotorResponseCode(Enum):
    """
    Response code of motor control APIs

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#response-content
    """

    SUCCESS = 0x00
    ERROR_TIMEOUT = 0x01
    ERROR_ID_MISSED = 0x02
    ERROR_INVALID_PARAMETER = 0x03
    ERROR_INVALID_CUBE_STATE = 0x04
    SUCCESS_WITH_OVERWRITE = 0x05
    ERROR_NOT_SUPPORTED = 0x06
    ERROR_FAILED_TO_APPEND = 0x07


class ResponseMotorControlTarget(CubeResponse):
    """
    Target specified motor control response

    Attributes:
        response_code (MotorResponseCode): Response code

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#responses-to-motor-control-with-target-specified
    """

    _payload_id = 0x83
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseMotorControlTarget._payload_id

    def __init__(self, payload: GattReadData):
        if ResponseMotorControlTarget.is_myself(payload):
            _, self.request_id, rc = self._converter.unpack_from(payload)
            self.response_code = MotorResponseCode(rc)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseMotorControlMultipleTargets(CubeResponse):
    """
    Multiple target specified motor control response

    Attributes:
        response_code (MotorResponseCode): Response code

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#responses-to-motor-control-with-multiple-targets-specified
    """

    _payload_id = 0x84
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseMotorControlMultipleTargets._payload_id

    def __init__(self, payload: GattReadData):
        if ResponseMotorControlMultipleTargets.is_myself(payload):
            _, self.request_id, rc = self._converter.unpack_from(payload)
            self.response_code = MotorResponseCode(rc)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


class ResponseMotorSpeed(CubeResponse):
    """
    Motor speed response

    Attributes:
        left (int): motor speed (left)
        right (int): motor speed (right)

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor#obtaining-motor-speed-information
    """

    _payload_id = 0xE0
    _converter = struct.Struct("<BBB")

    @staticmethod
    def is_myself(payload: GattReadData) -> bool:
        return payload[0] == ResponseMotorSpeed._payload_id

    def __init__(self, payload: GattReadData):
        if ResponseMotorSpeed.is_myself(payload):
            _, self.left, self.right = self._converter.unpack_from(payload)
        else:
            raise TypeError("wrong payload")

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


MotorResponseType: TypeAlias = Union[
    ResponseMotorControlTarget, ResponseMotorControlMultipleTargets, ResponseMotorSpeed
]
"""
Response types of motor characteristic
"""


class Motor(CubeCharacteristic):
    """
    Motor characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_motor
    """

    @staticmethod
    def is_my_data(payload: GattReadData) -> Optional[MotorResponseType]:
        if ResponseMotorControlTarget.is_myself(payload):
            return ResponseMotorControlTarget(payload)
        elif ResponseMotorControlMultipleTargets.is_myself(payload):
            return ResponseMotorControlMultipleTargets(payload)
        elif ResponseMotorSpeed.is_myself(payload):
            return ResponseMotorSpeed(payload)
        else:
            return None

    def __init__(self, interface: CubeInterface, device: NotificationReceivedDevice):
        self.interface = interface
        super().__init__(interface, ToioUuid.Motor.value, device)

    async def motor_control(
        self, left: int, right: int, duration_ms: Optional[int] = None
    ) -> None:
        """
        Send motor control command

        Args:
            left (int): Motor speed (left)
            right (int): Motor speed (right)
            duration_ms (Optional[int], optional): Motor driving period [ms]. Defaults to None.

        References:
            https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control
        """
        motor = MotorControl(left, right, duration_ms)
        await self._write_without_response(bytes(motor))

    async def motor_control_target(
        self,
        timeout: int,
        movement_type: Union[MovementType, int],
        speed: Union[Speed, Sequence[int]],
        target: Union[TargetPosition, Sequence[int]],
    ) -> None:
        """
        Send target specified motor control command

        Args:
            timeout (int): Timeout [s] (Note: not [ms])
            movement_type (MovementType): Movement type
            speed (Speed): Speed parameter
            target (TargetPosition): Target parameter

        References:
            https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control-with-target-specified
        """
        if isinstance(movement_type, int):
            movement_type = MovementType(movement_type)
        if isinstance(speed, Sequence):
            speed = Speed.from_int(*speed)
        if isinstance(target, Sequence):
            target = TargetPosition.from_int(*target)
        motor_target = MotorControlTarget(timeout, movement_type, speed, target)
        await self._write_without_response(bytes(motor_target))

    async def motor_control_multiple_targets(
        self,
        timeout: int,
        movement_type: Union[MovementType, int],
        speed: Union[Speed, Sequence[int]],
        mode: Union[WriteMode, int],
        target_list: Union[Sequence[TargetPosition], Sequence[Sequence[int]]],
    ) -> None:
        """
        Send multiple target specified motor control command

        Args:
            timeout (int): Timeout [s] (Note: not [ms])
            movement_type (Union[MovementType, int]): Movement type
            speed (Union[Speed, Sequence[int]]): Speed parameter
            mode (Union[WriteMode, int]): Write mode
            target_list (List[Union[TargetPosition, Sequence[int]]]): Target parameter list

        References:
            https://toio.github.io/toio-spec/en/docs/ble_motor#motor-control-with-multiple-targets-specified
        """
        if isinstance(movement_type, int):
            movement_type = MovementType(movement_type)
        if isinstance(speed, Sequence):
            speed = Speed.from_int(*speed)
        if isinstance(mode, int):
            mode = WriteMode(mode)
        targets: List[TargetPosition] = []
        for target in target_list:
            if isinstance(target, Sequence):
                targets.append(TargetPosition.from_int(*target))
            else:
                targets.append(target)
        motor_target = MotorControlMultipleTargets(
            timeout, movement_type, speed, mode, targets
        )
        await self._write_without_response(bytes(motor_target))

    async def motor_control_acceleration(
        self,
        translation: int,
        acceleration: int,
        rotation_velocity: int,
        rotation_direction: Union[AccelerationRotation, int],
        cube_direction: Union[AccelerationDirection, int],
        priority: Union[AccelerationPriority, int],
        duration_ms: int,
    ) -> None:
        """
        Send acceleration specified motor control command

        Args:
            translation (int): Speed at which the cube moves in relation to the direction of travel.
            acceleration (int): Specify the increment (or decrement) in speed every 100 milliseconds.
            rotation_velocity (int): Rotational velocity when the cube is changing orientation.
            rotation_direction (Union[AccelerationRotation, int]): Rotational direction when the cube is changing orientation.
            cube_direction (Union[AccelerationDirection, int]): Direction the cube travels.
            priority (Union[AccelerationPriority, int]): Priority to the translational speed or the rotational velocity.
            duration_ms (int): Motor driving period [ms].

        References:
            https://toio.github.io/toio-spec/en/docs/ble_motor/#motor-control-with-acceleration-specified
        """
        if isinstance(rotation_direction, int):
            rotation_direction = AccelerationRotation(rotation_direction)
        if isinstance(cube_direction, int):
            cube_direction = AccelerationDirection(cube_direction)
        if isinstance(priority, int):
            priority = AccelerationPriority(priority)
        motor_acceleration = MotorControlAcceleration(
            translation,
            acceleration,
            rotation_velocity,
            rotation_direction,
            cube_direction,
            priority,
            duration_ms,
        )
        await self._write_without_response(bytes(motor_acceleration))
