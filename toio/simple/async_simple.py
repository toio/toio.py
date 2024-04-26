# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/simple/async_simple.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import asyncio
import math
import time
from enum import Enum, auto
from logging import NOTSET, Formatter, NullHandler, StreamHandler, getLogger
from typing import ClassVar, Optional, Tuple, Type

from ..coordinate_systems import (
    LocalCoordinateSystem,
    VisualProgrammingCoordinateSystem,
)
from ..cube import ToioCoreCube
from ..cube.api.base_class import CubeCharacteristic, NotificationHandlerTypes
from ..cube.api.button import Button, ButtonInformation
from ..cube.api.configuration import (
    MagneticSensorCondition,
    MagneticSensorFunction,
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
)
from ..cube.api.id_information import (
    IdInformation,
    PositionId,
    PositionIdMissed,
    StandardId,
    StandardIdMissed,
)
from ..cube.api.indicator import Color, IndicatorParam
from ..cube.api.motor import (
    Motor,
    MotorResponseCode,
    MovementType,
    ResponseMotorControlMultipleTargets,
    ResponseMotorControlTarget,
    RotationOption,
    Speed,
    TargetPosition,
)
from ..cube.api.sensor import (
    MagneticSensorData,
    MotionDetectionData,
    PostureAngleEulerData,
    PostureDataType,
    Sensor,
)
from ..cube.api.sound import MidiNote, Note
from ..position import (
    STAY_CURRENT,
    CubeLocation,
    MatRect,
    Point,
    RelativeCubeLocation,
    ToioMat,
)
from ..scanner.ble import UniversalBleScanner
from ..standard_id import StandardIdCard
from ..utility import clip

module_logger = getLogger(__name__)
module_logger.setLevel(NOTSET)
module_handler = NullHandler()
module_handler.setLevel(NOTSET)
module_logger.addHandler(module_handler)


class Direction(Enum):
    Forward = auto()
    Backward = auto()
    Right = auto()
    Left = auto()


class AsyncSimpleCube:
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
    _LOCK: Optional[asyncio.Lock] = None
    _CUBES: int = 0

    @staticmethod
    def ensure_event_loop() -> asyncio.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            return event_loop

    @classmethod
    async def search(cls, name: Optional[str] = None, timeout: int = 5) -> ToioCoreCube:
        BLEScanner = UniversalBleScanner()
        if name is not None:
            module_logger.info(f"search {name} in my registered devices")
            devices = await BLEScanner.scan_registered_cubes_with_id(cube_id={name})
            if len(devices) == 0:
                module_logger.info(f"search {name}")
                devices = await BLEScanner.scan_with_id(cube_id={name})
        else:
            module_logger.info("scan registered devices")
            devices = await BLEScanner.scan_registered_cubes(1, timeout=timeout)
            if len(devices) == 0:
                module_logger.info("scan all devices")
                devices = await BLEScanner.scan(1, timeout=timeout)
                module_logger.info("scan complete")
                module_logger.debug(devices)

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
        cube: Optional[ToioCoreCube] = None,
    ) -> None:
        if AsyncSimpleCube._LOCK is None:
            AsyncSimpleCube._LOCK = asyncio.Lock()

        self.logger = getLogger(__name__ + str(AsyncSimpleCube._CUBES))
        AsyncSimpleCube._CUBES += 1

        if log_level is not NOTSET:
            self.logger.setLevel(log_level)
            log_handler = StreamHandler()
            formatter = Formatter(
                "simple:"
                + str(AsyncSimpleCube._CUBES)
                + ":%(asctime)s %(levelname)7s %(message)s"
            )
            log_handler.setFormatter(formatter)
            log_handler.setLevel(log_level)
            self.logger.addHandler(log_handler)

        self.logger.info("initialized")

        self._native_location: Optional[CubeLocation] = None
        self._location: Optional[RelativeCubeLocation] = None
        self._standard_id: Optional[StandardId] = None
        self._on_position_id: bool = False
        self._on_standard_id: bool = False
        self._mat: Optional[MatRect] = None
        self._arrived: bool = False
        self._name: Optional[str] = name
        self._timeout: int = timeout
        self._coordinate_system_class: Type[LocalCoordinateSystem] = (
            coordinate_system_class
        )
        self._cube = cube

        self._motion: Optional[MotionDetectionData] = None
        self._cube_angle: Optional[PostureAngleEulerData] = None
        self._magnet: Optional[MagneticSensorData] = None

    async def _scan(self) -> None:
        if self._cube is None:
            self._cube = await self.search(name=self._name, timeout=self._timeout)
        if self._cube is None:
            raise Exception("no cubes are found")

    async def _setup(self) -> None:
        assert self._cube is not None
        self._button: Optional[ButtonInformation] = await self._cube.api.button.read()
        await self._set_sensor_configurations()
        await self._request_initial_information()

        handlers: Tuple[Tuple[CubeCharacteristic, NotificationHandlerTypes], ...] = (
            (self._cube.api.id_information, self._id_notification_handler),
            (self._cube.api.motor, self._motor_notification_handler),
            (self._cube.api.sensor, self._motion_sensor_notification_handler),
            (self._cube.api.button, self._button_notification_handler),
        )
        for characteristic, notification_handler in handlers:
            await characteristic.register_notification_handler(notification_handler)
        await self._wait_to_obtain_initial_information()

    async def _set_sensor_configurations(self) -> None:
        assert self._cube is not None
        await self._cube.api.configuration.set_magnetic_sensor(
            function_type=MagneticSensorFunction.MagnetState,
            # function_type=MagneticSensorFunction.MagneticForce,
            interval_ms=60,
            condition=MagneticSensorCondition.ChangeDetection,
        )
        await self._cube.api.configuration.set_posture_angle_detection(
            detection_type=PostureAngleDetectionType.Euler,
            interval_ms=50,
            condition=PostureAngleDetectionCondition.ChangeDetection,
        )

    async def _request_initial_information(self) -> None:
        assert self._cube is not None
        await self._cube.api.sensor.request_motion_information()
        await self._cube.api.sensor.request_posture_angle_information(
            PostureDataType.Euler
        )
        await self._cube.api.sensor.request_magnetic_sensor_information()

    async def _wait_to_obtain_initial_information(self):
        while not self._motion or not self._cube_angle or not self._magnet:
            await self._request_initial_information()
            await asyncio.sleep(0.1)

    def __del__(self) -> None:
        AsyncSimpleCube._CUBES -= 1

    async def __aenter__(self) -> AsyncSimpleCube:
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        self.logger.info("start to connect")
        assert AsyncSimpleCube._LOCK is not None
        self.logger.info("try to lock")
        async with AsyncSimpleCube._LOCK:
            self.logger.info("enter critical section")
            self.logger.info("scanning")
            await self._scan()
            assert self._cube is not None
            self.logger.info("connecting")
            await self._cube.connect()
            self.logger.info("connected (%s)", self._cube.name)
            await self._setup()
            self.logger.info("setup completed")
            self.logger.info("exit critical section")
        self.logger.info("release lock")
        await asyncio.sleep(0)

    async def disconnect(self) -> None:
        assert self._cube is not None
        self.logger.debug("disconnecting")
        if self._cube.is_connect():
            await self._cube.disconnect()
        self.logger.debug("disconnected")

    async def sleep(self, sleep_second: float) -> None:
        start_time = time.time()
        while True:
            await asyncio.sleep(0)
            time.sleep(0)
            if (time.time() - start_time) >= sleep_second:
                break

    async def _id_notification_handler(self, payload: bytearray) -> None:
        id_info = IdInformation.is_my_data(payload)
        self.logger.debug(id_info)
        if isinstance(id_info, PositionId):
            self._native_location = id_info.center
            for mat in ToioMat.mats:
                if self._native_location.point in mat:
                    if mat != self._mat:
                        self.logger.debug(str(mat))
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

    async def _motor_notification_handler(self, payload: bytearray) -> None:
        motor_response = Motor.is_my_data(payload)
        self.logger.debug(motor_response)
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

    async def _motion_sensor_notification_handler(self, payload: bytearray) -> None:
        sensor_info = Sensor.is_my_data(payload)
        self.logger.debug(sensor_info)
        if isinstance(sensor_info, MotionDetectionData):
            self._motion = sensor_info
        elif isinstance(sensor_info, PostureAngleEulerData):
            self._cube_angle = sensor_info
        elif isinstance(sensor_info, MagneticSensorData):
            self._magnet = sensor_info

    async def _button_notification_handler(self, payload: bytearray) -> None:
        button_info = Button.is_my_data(payload)
        self.logger.debug(button_info)
        if isinstance(button_info, ButtonInformation):
            self._button = button_info

    async def move(
        self, speed: int, duration: float, wait_to_complete: bool = True
    ) -> None:
        assert self._cube is not None
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        await self._cube.api.motor.motor_control(speed, speed, duration_ms)
        if wait_to_complete:
            await self.sleep(duration)

    async def spin(
        self, speed: int, duration: float, wait_to_complete: bool = True
    ) -> None:
        """
        speed: (negative value: anticlockwise)
        """
        assert self._cube is not None
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        await self._cube.api.motor.motor_control(speed, -speed, duration_ms)
        if wait_to_complete:
            await self.sleep(duration)

    async def run_motor(
        self,
        left_speed: int,
        right_speed: int,
        duration: float,
        wait_to_complete: bool = True,
    ) -> None:
        assert self._cube is not None
        duration = max(duration, 0)
        duration_ms = int(duration * 1000)
        await self._cube.api.motor.motor_control(left_speed, right_speed, duration_ms)
        if wait_to_complete:
            await self.sleep(duration)

    async def stop_motor(self) -> None:
        """stop_motor.

        Args:

        Returns:
            None:
        """
        assert self._cube is not None
        await self._cube.api.motor.motor_control(0, 0)

    async def move_steps(self, direction: Direction, speed: int, step: int) -> bool:
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
        return await self._wait_arrival(
            await self._move_to_target(speed_param, target_param)
        )

    def _step_to_point(self, step: int) -> int:
        return step * self.DEFAULT_ONE_STEP

    async def _move_to_target(self, speed: Speed, target: TargetPosition) -> float:
        assert self._cube is not None
        self._arrived = False
        executed_time = time.time()
        await self._cube.api.motor.motor_control_target(
            timeout=self.DEFAULT_TIMEOUT,
            movement_type=self.DEFAULT_MOVEMENT_TYPE,
            speed=speed,
            target=target,
        )
        return executed_time

    async def _wait_arrival(self, executed_time: float):
        while not self._arrived:
            if not self._on_position_id:
                self.logger.debug("Position ID Missed")
                return False
            elif time.time() - executed_time < self.DEFAULT_TIMEOUT:
                await asyncio.sleep(self.MONITORING_CYCLE)
            else:
                break
        return self._arrived

    async def turn(self, speed: int, degree: int) -> bool:
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
        return await self._wait_arrival(
            await self._move_to_target(speed_param, target_param)
        )

    async def move_to(self, speed: int, x: int, y: int) -> bool:
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
        return await self._wait_arrival(
            await self._move_to_target(speed_param, target_param)
        )

    async def set_orientation(self, speed: int, degree: int) -> bool:
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
        return await self._wait_arrival(
            await self._move_to_target(speed_param, target_param)
        )

    async def move_to_the_grid_cell(self, speed: int, cell_x: int, cell_y: int) -> bool:
        if not self._on_position_id:
            return False
        cell_point = self._cell_to_point(cell_x, cell_y)
        return await self.move_to(speed, cell_point.x, cell_point.y)

    async def get_current_position(self) -> Optional[Tuple[int, int]]:
        if self._location:
            return (
                self._location.relative_location.point.x,
                self._location.relative_location.point.y,
            )
        else:
            return None

    async def get_x(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.point.x
        else:
            return None

    async def get_y(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.point.y
        else:
            return None

    async def get_orientation(self) -> Optional[int]:
        if self._location:
            return self._location.relative_location.angle
        else:
            return None

    async def get_grid(self) -> Optional[Tuple[int, int]]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (cell_x, cell_y) = self._point_to_cell(self._location.relative_location.point)
        return cell_x, cell_y

    async def get_grid_x(self) -> Optional[int]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (cell_x, _) = self._point_to_cell(self._location.relative_location.point)
        return cell_x

    async def get_grid_y(self) -> Optional[int]:
        if not self._on_position_id:
            return None
        assert self._location is not None
        (_, cell_y) = self._point_to_cell(self._location.relative_location.point)
        return cell_y

    async def is_on_the_gird_cell(self, cell_x: int, cell_y: int) -> bool:
        if not self._on_position_id:
            return False
        assert self._location is not None
        (current_cell_x, current_cell_y) = self._point_to_cell(
            self._location.relative_location.point
        )
        return (cell_x, cell_y) == (current_cell_x, current_cell_y)

    def _cell_to_point(self, cell_x: int, cell_y: int) -> Point:
        return Point(x=round(self.CELL_SIZE * cell_x), y=round(self.CELL_SIZE * cell_y))

    def _point_to_cell(self, relative_point: Point) -> Tuple[int, int]:
        cell = relative_point / self.CELL_SIZE
        return cell.x, cell.y

    async def is_touched(self, item: StandardIdCard) -> bool:
        if not self._standard_id:
            return False
        try:
            current_item = StandardIdCard(self._standard_id.value)
        except ValueError:
            self.logger.debug(
                f"ValueError: Wrong Standard ID is detected:{self._standard_id.value}"
            )
            return False
        return current_item == item

    async def get_touched_card(self) -> Optional[int]:
        if not self._standard_id:
            return None
        try:
            current_item: Enum = StandardIdCard(self._standard_id.value)
        except ValueError:
            self.logger.debug(
                f"ValueError: Wrong Standard ID is detected:{self._standard_id.value}"
            )
            return None
        self.logger.info(current_item.name)
        return current_item.value

    async def get_cube_name(self) -> Optional[str]:
        assert self._cube is not None
        return self._cube.name

    async def get_battery_level(self) -> Optional[int]:
        assert self._cube is not None
        battery_info = await self._cube.api.battery.read()
        if battery_info is not None:
            return battery_info.battery_level
        else:
            return None

    async def get_3d_angle(self) -> Optional[Tuple[int, int, int]]:
        if self._cube_angle is None:
            return None
        return self._cube_angle.roll, self._cube_angle.pitch, self._cube_angle.yaw

    async def get_posture(self) -> Optional[int]:
        if self._motion is None:
            return None
        else:
            return self._motion.posture.value

    async def is_button_pressed(self) -> Optional[int]:
        if self._button is None:
            return None
        else:
            return self._button.state

    async def turn_on_cube_lamp(self, r: int, g: int, b: int, duration: float) -> None:
        assert self._cube is not None
        duration = max(duration, 0)
        indicator_param = IndicatorParam(
            duration_ms=0,
            color=Color(r=r, g=g, b=b),
        )
        await self._cube.api.indicator.turn_on(indicator_param)
        if duration > 0:
            await self.sleep(duration)
            await self._cube.api.indicator.turn_off_all()

    async def turn_off_cube_lamp(self) -> None:
        assert self._cube is not None
        await self._cube.api.indicator.turn_off_all()

    async def play_sound(
        self, note: int, duration: float, wait_to_complete: bool = True
    ) -> bool:
        assert self._cube is not None
        duration_ms = clip(int(duration * 1000), 1, 2550)
        try:
            note_name = Note(note)
        except ValueError:
            self.logger.debug(f"ValueError: note number {note} is unsupported")
            return False
        midi_notes = [
            MidiNote(
                duration_ms=duration_ms,
                note=note_name,
                volume=255,
            )
        ]
        await self._cube.api.sound.play_midi(
            repeat=1,
            midi_notes=midi_notes,
        )
        if wait_to_complete:
            await self.sleep(duration)
        return True

    async def stop_sound(self) -> None:
        assert self._cube is not None
        await self._cube.api.sound.stop()

    async def is_magnet_in_contact(self) -> Optional[int]:
        if self._magnet is None:
            return None
        else:
            return self._magnet.state
