#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_motor.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio

import pytest

from toio import (
    AccelerationDirection,
    AccelerationPriority,
    AccelerationRotation,
    BLEScanner,
    CubeLocation,
    Motor,
    MotorResponseCode,
    MovementType,
    Point,
    ResponseMotorControlMultipleTargets,
    ResponseMotorControlTarget,
    RotationOption,
    Speed,
    SpeedChangeType,
    TargetPosition,
    ToioCoreCube,
    WriteMode,
)


async def cube_connect():
    device_list = await BLEScanner.scan(1)
    assert len(device_list) > 0
    cube = ToioCoreCube(device_list[0].interface)
    await cube.connect()
    return cube


async def cube_disconnect(cube):
    await cube.disconnect()
    await asyncio.sleep(2)


RESPONSE_TARGET = None
RESPONSE_MULTIPLE_TARGET = None


def notification_handler(payload: bytearray):
    motor_info = Motor.is_my_data(payload)
    print(type(motor_info), str(motor_info))
    if isinstance(motor_info, ResponseMotorControlTarget):
        global RESPONSE_TARGET
        RESPONSE_TARGET = motor_info
    elif isinstance(motor_info, ResponseMotorControlMultipleTargets):
        global RESPONSE_MULTIPLE_TARGET
        RESPONSE_MULTIPLE_TARGET = motor_info


@pytest.mark.asyncio
async def test_motor_1():
    cube = await cube_connect()
    await cube.api.motor.motor_control(10, 10)
    await asyncio.sleep(2)
    await cube.api.motor.motor_control(0, 0)
    await cube_disconnect(cube)


@pytest.mark.asyncio
async def test_motor_2():
    global RESPONSE_TARGET
    global RESPONSE_MULTIPLE_TARGET
    RESPONSE_TARGET = None
    RESPONSE_MULTIPLE_TARGET = None

    cube = await cube_connect()
    await cube.api.motor.register_notification_handler(notification_handler)
    await cube.api.motor.motor_control_target(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(
            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
        ),
        target=TargetPosition(
            cube_location=CubeLocation(point=Point(x=350, y=170), angle=0),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
    )

    await asyncio.sleep(4)
    await cube.api.motor.motor_control(0, 0)
    await cube_disconnect(cube)

    assert RESPONSE_TARGET is not None
    assert RESPONSE_TARGET.response_code == MotorResponseCode.SUCCESS


@pytest.mark.asyncio
async def test_motor_3():
    global RESPONSE_TARGET
    global RESPONSE_MULTIPLE_TARGET
    RESPONSE_TARGET = None
    RESPONSE_MULTIPLE_TARGET = None

    cube = await cube_connect()
    await cube.api.motor.register_notification_handler(notification_handler)
    targets = [
        TargetPosition(
            cube_location=CubeLocation(point=Point(x=250, y=170), angle=135),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
        TargetPosition(
            cube_location=CubeLocation(point=Point(x=120, y=210), angle=0),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
    ]
    await cube.api.motor.motor_control_multiple_targets(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(
            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
        ),
        mode=WriteMode.Overwrite,
        target_list=targets,
    )

    await asyncio.sleep(5)
    await cube_disconnect(cube)

    assert RESPONSE_MULTIPLE_TARGET is not None
    assert RESPONSE_MULTIPLE_TARGET.response_code == MotorResponseCode.SUCCESS


@pytest.mark.asyncio
async def test_motor_4():
    cube = await cube_connect()

    await cube.api.motor.motor_control_acceleration(
        translation=100,
        acceleration=5,
        rotation_velocity=0,
        rotation_direction=AccelerationRotation.Positive,
        cube_direction=AccelerationDirection.Forward,
        priority=AccelerationPriority.TranslationalVelocity,
        duration_ms=2000,
    )

    await asyncio.sleep(4)
    await cube_disconnect(cube)
