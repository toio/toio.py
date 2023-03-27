# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/simple/__init__.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import asyncio
import math
import time
from enum import Enum, auto
from logging import NOTSET, NullHandler, StreamHandler, getLogger
from typing import ClassVar, Optional, Type

from toio.coordinate_systems import (
    LocalCoordinateSystem,
    VisualProgrammingCoordinateSystem,
)
from toio.cube import ToioCoreCube
from toio.cube.api.base_class import CubeCharacteristic, CubeNotificationHandler
from toio.cube.api.button import Button, ButtonInformation
from toio.cube.api.configuration import (
    MagneticSensorCondition,
    MagneticSensorFunction,
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
)
from toio.cube.api.id_information import (
    IdInformation,
    PositionId,
    PositionIdMissed,
    StandardId,
    StandardIdMissed,
)
from toio.cube.api.indicator import Color, IndicatorParam
from toio.cube.api.motor import (
    Motor,
    MotorResponseCode,
    MovementType,
    ResponseMotorControlMultipleTargets,
    ResponseMotorControlTarget,
    RotationOption,
    Speed,
    TargetPosition,
)
from toio.cube.api.sensor import (
    MagneticSensorData,
    MotionDetectionData,
    PostureAngleEulerData,
    PostureDataType,
    Sensor,
)
from toio.cube.api.sound import MidiNote, Note
from toio.position import (
    STAY_CURRENT,
    CubeLocation,
    MatRect,
    Point,
    RelativeCubeLocation,
    ToioMat,
)
from toio.scanner import BLEScanner
from toio.standard_id import StandardIdCard
from toio.utility import clip

logger = getLogger(__name__)
logger.setLevel(NOTSET)
handler = NullHandler()
handler.setLevel(NOTSET)
logger.addHandler(handler)


class Direction(Enum):
    Forward = auto()
    Backward = auto()
    Right = auto()
    Left = auto()


class SimpleCube(object):
    """
    Access to toio core cube by easier method
    Functions that like blocks in visual programming
    """

    DEFAULT_ROTATION_OPTION: ClassVar[RotationOption] = RotationOption.AbsoluteOptimal
    DEFAULT_MOVEMENT_TYPE: ClassVar[MovementType] = MovementType.Curve
    DEFAULT_TIMEOUT: ClassVar[int] = 10
    DEFAULT_ONE_STEP: ClassVar[int] = 1
    CELL_SIZE: ClassVar[float] = 43.43
    MONITORING_CYCLE: ClassVar[float] = 0.01

    @classmethod
    async def search(cls, name: Optional[str] = None, timeout: int = 5) -> ToioCoreCube:
        if name is not None:
            logger.info(f"search {name} in my registered devices")
            devices = await BLEScanner.scan_registered_cubes_with_id(cube_id={name})
            if len(devices) == 0:
                logger.info(f"search {name}")
                devices = await BLEScanner.scan_with_id(cube_id={name})
        else:
            logger.info("scan registered devices")
            devices = await BLEScanner.scan_registered_cubes(1, timeout=timeout)
            if len(devices) == 0:
                logger.info("scan all devices")
                devices = await BLEScanner.scan(1, timeout=timeout)
                logger.info("scan complete")
                logger.debug(devices)
        if len(devices) != 1:
            raise ValueError
        return ToioCoreCube(interface=devices[0].interface, name=devices[0].name)

    def __init__(
        self,
        name: Optional[str] = None,
        timeout: int = 5,
        coordinate_system_class: Type[
            LocalCoordinateSystem
        ] = VisualProgrammingCoordinateSystem,
        log_level: int = NOTSET,
    ) -> None:
        self._native_location: Optional[CubeLocation] = None
        self._location: Optional[RelativeCubeLocation] = None
        self._standard_id: Optional[StandardId] = None
        self._on_position_id: bool = False
        self._on_standard_id: bool = False
        self._mat: Optional[MatRect] = None
        self._arrived: bool = False
        self._coordinate_system_class: Type[
            LocalCoordinateSystem
        ] = coordinate_system_class
        if log_level is not NOTSET:
            logger.setLevel(log_level)
            log_handler = StreamHandler()
            log_handler.setLevel(log_level)
            logger.addHandler(log_handler)
        self._event_loop = asyncio.get_event_loop()
        self._cube: ToioCoreCube = self._event_loop.run_until_complete(
            self.search(name=name, timeout=timeout)
        )
        self._motion: Optional[MotionDetectionData] = None
        self._cube_angle: Optional[PostureAngleEulerData] = None
        self._magnet: Optional[MagneticSensorData] = None

        logger.debug("connecting")
        self._event_loop.run_until_complete(self._cube.connect())
        logger.debug(f"connected ({self._cube.name})")

        self._button: Optional[ButtonInformation] = self._event_loop.run_until_complete(
            self._cube.api.button.read()
        )
        self._set_sensor_configurations()
        self._request_initial_information()

        handlers: tuple[tuple[CubeCharacteristic, CubeNotificationHandler], ...] = (
            (self._cube.api.id_information, self._id_notification_handler),
            (self._cube.api.motor, self._motor_notification_handler),
            (self._cube.api.sensor, self._motion_sensor_notification_handler),
            (self._cube.api.button, self._button_notification_handler),
        )
        for characteristic, notification_handler in handlers:
            self._event_loop.run_until_complete(
                characteristic.register_notification_handler(notification_handler)
            )
        self._wait_to_obtain_initial_information()

    def _set_sensor_configurations(self):
        self._event_loop.run_until_complete(
            self._cube.api.configuration.set_magnetic_sensor(
                function_type=MagneticSensorFunction.MagnetState,
                # function_type=MagneticSensorFunction.MagneticForce,
                interval_ms=60,
                condition=MagneticSensorCondition.ChangeDetection,
            )
        )
        self._event_loop.run_until_complete(
            self._cube.api.configuration.set_posture_angle_detection(
                detection_type=PostureAngleDetectionType.Euler,
                interval_ms=50,
                condition=PostureAngleDetectionCondition.ChangeDetection,
            )
        )

    def _request_initial_information(self):
        self._event_loop.run_until_complete(
            self._cube.api.sensor.request_motion_information()
        )
        self._event_loop.run_until_complete(
            self._cube.api.sensor.request_posture_angle_information(
                PostureDataType.Euler
            )
        )
        self._event_loop.run_until_complete(
            self._cube.api.sensor.request_magnetic_sensor_information()
        )

    def _wait_to_obtain_initial_information(self):
        while not self._motion or not self._cube_angle or not self._magnet:
            self._request_initial_information()
            self._event_loop.run_until_complete(asyncio.sleep(0.1))

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.disconnect()

    def disconnect(self):
        logger.debug("disconnecting")
        self._event_loop.run_until_complete(self._cube.disconnect())
        logger.debug("disconnected")

    def sleep(self, sleep_second: float):
        self._event_loop.run_until_complete(asyncio.sleep(sleep_second))

    def _id_notification_handler(self, payload: bytearray) -> None:
        id_info = IdInformation.is_my_data(payload)
        logger.debug(id_info)
        if isinstance(id_info, PositionId):
            self._native_location = id_info.center
            for mat in ToioMat.mats:
                if self._native_location.point in mat:
                    if mat != self._mat:
                        logger.debug(str(mat))
                        self._mat = mat
                        self._location = RelativeCubeLocation.new()
                        coordinate_system = self._coordinate_system_class(
                            origin=mat.center()
                        )
                        self._location.change_coordinate_system(coordinate_system)
                    else:
                        assert self._location is not None
                    self._location.from_absolute_location(self._native_location)
                    break
            assert self._location is not None
            self._on_position_id = True
        elif isinstance(id_info, StandardId):
            coordinate_system = self._coordinate_system_class()
            id_info.angle = coordinate_system.from_native_angle(id_info.angle)
            self._standard_id = id_info
            self._on_standard_id = True
        elif isinstance(id_info, PositionIdMissed):
            self._location = None
            self._mat = None
            self._native_location = None
            self._on_position_id = False
        elif isinstance(id_info, StandardIdMissed):
            self._standard_id = None
            self._on_standard_id = False

    def _motor_notification_handler(self, payload: bytearray) -> None:
        motor_response = Motor.is_my_data(payload)
        logger.debug(motor_response)
        if isinstance(
            motor_response,
            (ResponseMotorControlTarget, ResponseMotorControlMultipleTargets),
        ):
            if (
                motor_response.response_code == MotorResponseCode.SUCCESS
                or motor_response.response_code
                == MotorResponseCode.SUCCESS_WITH_OVERWRITE
            ):
                self._arrived = True

    def _motion_sensor_notification_handler(self, payload: bytearray) -> None:
        sensor_info = Sensor.is_my_data(payload)
        logger.debug(sensor_info)
        if isinstance(sensor_info, MotionDetectionData):
            self._motion = sensor_info
        elif isinstance(sensor_info, PostureAngleEulerData):
            self._cube_angle = sensor_info
        elif isinstance(sensor_info, MagneticSensorData):
            self._magnet = sensor_info

    def _button_notification_handler(self, payload: bytearray) -> None:
        button_info = Button.is_my_data(payload)
        logger.debug(button_info)
        if isinstance(button_info, ButtonInformation):
            self._button = button_info

    def move(self, speed: int, duration: float, wait_to_complete: bool = True) -> None:
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        self._event_loop.run_until_complete(
            self._cube.api.motor.motor_control(speed, speed, duration_ms)
        )
        if wait_to_complete:
            self.sleep(duration)

    def spin(self, speed: int, duration: float, wait_to_complete: bool = True) -> None:
        """
        speed: (negative value: anticlockwise)
        """
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        self._event_loop.run_until_complete(
            self._cube.api.motor.motor_control(speed, -speed, duration_ms)
        )
        if wait_to_complete:
            self.sleep(duration)

    def run_motor(
        self,
        left_speed: int,
        right_speed: int,
        duration: float,
        wait_to_complete: bool = True,
    ) -> None:
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        self._event_loop.run_until_complete(
            self._cube.api.motor.motor_control(left_speed, right_speed, duration_ms)
        )
        if wait_to_complete:
            self.sleep(duration)

    def stop_motor(self) -> None:
        self._event_loop.run_until_complete(self._cube.api.motor.motor_control(0, 0))

    def move_steps(self, direction: Direction, speed: int, step: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._native_location is not None
        if direction == Direction.Forward:
            distance = self._step_to_point(step)
        elif direction == Direction.Backward:
            distance = -1 * self._step_to_point(step)
        else:
            return False
        native_location = self._native_location
        target_x = native_location.point.x + round(
            distance * math.cos(math.radians(native_location.angle))
        )
        target_y = native_location.point.y + round(
            distance * math.sin(math.radians(native_location.angle))
        )
        target_location = CubeLocation(
            point=Point(x=target_x, y=target_y), angle=native_location.angle
        )
        boundary_location = native_location.get_boundary_point(target_location)
        target_param = TargetPosition(
            cube_location=boundary_location,
            rotation_option=RotationOption.WithoutRotation,
        )
        speed_param = Speed(
            max=clip(abs(speed), 0, 255),
        )
        return self._wait_arrival(self._move_to_target(speed_param, target_param))

    def _step_to_point(self, step: int) -> int:
        return step * self.DEFAULT_ONE_STEP

    def _move_to_target(self, speed: Speed, target: TargetPosition) -> float:
        self._arrived = False
        executed_time = time.time()
        self._event_loop.run_until_complete(
            self._cube.api.motor.motor_control_target(
                timeout=self.DEFAULT_TIMEOUT,
                movement_type=self.DEFAULT_MOVEMENT_TYPE,
                speed=speed,
                target=target,
            )
        )
        return executed_time

    def _wait_arrival(self, executed_time: float):
        while not self._arrived:
            if not self._on_position_id:
                logger.debug("Position ID Missed")
                return False
            elif time.time() - executed_time < self.DEFAULT_TIMEOUT:
                self._event_loop.run_until_complete(
                    asyncio.sleep(self.MONITORING_CYCLE)
                )
            else:
                break
        return self._arrived

    def turn(self, speed: int, degree: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._location is not None
        if degree >= 0:
            rotation = RotationOption.RelativePositive
        else:
            rotation = RotationOption.RelativeNegative
            degree = -1 * degree
        current_location = CubeLocation(
            point=Point(x=STAY_CURRENT, y=STAY_CURRENT), angle=degree
        )
        target_param = TargetPosition(
            cube_location=current_location,
            rotation_option=rotation,
        )
        speed_param = Speed(
            max=clip(abs(speed), 0, 255),
        )
        return self._wait_arrival(self._move_to_target(speed_param, target_param))

    def move_to(self, speed: int, x: int, y: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._native_location is not None
        assert self._location is not None
        relative_location = self._location
        relative_location.relative_location = CubeLocation(
            point=Point(x=x, y=y), angle=0
        )
        boundary_location = self._native_location.get_boundary_point(
            relative_location.to_absolute_location()
        )
        target_param = TargetPosition(
            cube_location=boundary_location,
            rotation_option=RotationOption.WithoutRotation,
        )
        speed_param = Speed(
            max=clip(abs(speed), 0, 255),
        )
        return self._wait_arrival(self._move_to_target(speed_param, target_param))

    def set_orientation(self, speed: int, degree: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._native_location is not None
        if degree >= 0:
            rotation = RotationOption.AbsolutePositive
        else:
            rotation = RotationOption.AbsoluteNegative
            degree = -1 * degree
        coordinate_system = self._coordinate_system_class()
        degree = round(coordinate_system.to_native_angle(degree))
        current_location = CubeLocation(
            point=Point(x=STAY_CURRENT, y=STAY_CURRENT), angle=degree
        )
        target_param = TargetPosition(
            cube_location=current_location,
            rotation_option=rotation,
        )
        speed_param = Speed(
            max=clip(abs(speed), 0, 255),
        )
        return self._wait_arrival(self._move_to_target(speed_param, target_param))

    def move_to_the_grid_cell(self, speed: int, cell_x: int, cell_y: int) -> bool:
        if not self._on_position_id:
            return False
        cell_point = self._cell_to_point(cell_x, cell_y)
        return self.move_to(speed, cell_point.x, cell_point.y)

    def get_current_position(self) -> Optional[tuple[int, int]]:
        if self._location:
            return (
                self._location.relative_location.point.x,
                self._location.relative_location.point.y,
            )
        else:
            return None

    def get_x(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.point.x
        else:
            return None

    def get_y(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.point.y
        else:
            return None

    def get_orientation(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.angle
        else:
            return None

    def get_grid(self) -> Optional[tuple[int, int]]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (cell_x, cell_y) = self._point_to_cell(self._location.relative_location.point)
        return cell_x, cell_y

    def get_grid_x(self) -> Optional[int]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (cell_x, _) = self._point_to_cell(self._location.relative_location.point)
        return cell_x

    def get_grid_y(self) -> Optional[int]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (_, cell_y) = self._point_to_cell(self._location.relative_location.point)
        return cell_y

    def is_on_the_gird_cell(self, cell_x: int, cell_y: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._location is not None
        (current_cell_x, current_cell_y) = self._point_to_cell(
            self._location.relative_location.point
        )
        return (cell_x, cell_y) == (current_cell_x, current_cell_y)

    def _cell_to_point(self, cell_x: int, cell_y: int) -> Point:
        return Point(x=round(self.CELL_SIZE * cell_x), y=round(self.CELL_SIZE * cell_y))

    def _point_to_cell(self, relative_point: Point) -> tuple[int, int]:
        cell = relative_point / self.CELL_SIZE
        return cell.x, cell.y

    def is_touched(self, item: StandardIdCard) -> bool:
        if not self._standard_id:
            return False
        try:
            current_item = StandardIdCard(self._standard_id.value)
        except ValueError:
            logger.debug(
                f"ValueError: Wrong Standard ID is detected:{self._standard_id.value}"
            )
            return False
        return current_item == item

    def get_touched_card(self) -> Optional[int]:
        if not self._standard_id:
            return None
        try:
            current_item: Enum = StandardIdCard(self._standard_id.value)
        except ValueError:
            logger.debug(
                f"ValueError: Wrong Standard ID is detected:{self._standard_id.value}"
            )
            return None
        logger.info(current_item.name)
        return current_item.value

    def get_cube_name(self) -> Optional[str]:
        return self._cube.name

    def get_battery_level(self) -> Optional[int]:
        battery_info = self._event_loop.run_until_complete(
            self._cube.api.battery.read()
        )
        if battery_info is not None:
            return battery_info.battery_level
        else:
            return None

    def get_3d_angle(self) -> Optional[tuple[int, int, int]]:
        if self._cube_angle is None:
            return None
        return self._cube_angle.roll, self._cube_angle.pitch, self._cube_angle.yaw

    def get_posture(self) -> Optional[int]:
        if self._motion is None:
            return None
        else:
            return self._motion.posture.value

    def is_button_pressed(self) -> Optional[int]:
        if self._button is None:
            return None
        else:
            return self._button.state

    def turn_on_cube_lamp(self, r: int, g: int, b: int, duration: float) -> None:
        duration = max(duration, 0)
        indicator_param = IndicatorParam(
            duration_ms=0,
            color=Color(r=r, g=g, b=b),
        )
        self._event_loop.run_until_complete(
            self._cube.api.indicator.turn_on(indicator_param)
        )
        if duration > 0:
            self.sleep(duration)
            self._event_loop.run_until_complete(self._cube.api.indicator.turn_off_all())

    def turn_off_cube_lamp(self) -> None:
        self._event_loop.run_until_complete(self._cube.api.indicator.turn_off_all())

    def play_sound(
        self, note: int, duration: float, wait_to_complete: bool = True
    ) -> bool:
        duration_ms = clip(int(duration * 100), 1, 255)
        try:
            note_name = Note(note)
        except ValueError:
            logger.debug(f"ValueError: note number {note} is unsupported")
            return False
        midi_notes = [
            MidiNote(
                duration_ms=duration_ms,
                note=note_name,
                volume=255,
            )
        ]
        self._event_loop.run_until_complete(
            self._cube.api.sound.play_midi(
                repeat=1,
                midi_notes=midi_notes,
            )
        )
        if wait_to_complete:
            self.sleep(duration)
        return True

    def stop_sound(self) -> None:
        self._event_loop.run_until_complete(self._cube.api.sound.stop())

    def is_magnet_in_contact(self) -> Optional[int]:
        if self._magnet is None:
            return None
        else:
            return self._magnet.state
