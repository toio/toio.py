#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     motor_control.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio

from toio import *


def notification_handler(payload: bytearray):
    motor_info = Motor.is_my_data(payload)
    print(type(motor_info), str(motor_info))


async def test_motor_1():
    """
    example ToioCoreCube.api.motor.motor_control()
    """
    async with ToioCoreCube() as cube:
        await cube.api.motor.motor_control(10, 10)
        await asyncio.sleep(2)
        await cube.api.motor.motor_control(0, 0)


async def test_motor_2():
    """
    example ToioCoreCube.api.motor.motor_control_target()
    """
    async with ToioCoreCube() as cube:
        await cube.api.motor.register_notification_handler(notification_handler)
        await cube.api.motor.motor_control_target(
            timeout=5,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
            ),
            target=TargetPosition(
                cube_location=CubeLocation(point=Point(x=200, y=200), angle=0),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )

        await asyncio.sleep(4)
        await cube.api.motor.motor_control(0, 0)


async def test_motor_3():
    """
    example ToioCoreCube.api.motor.motor_control_multiple_targets()
    """
    async with ToioCoreCube() as cube:
        await cube.api.motor.register_notification_handler(notification_handler)
        targets = [
            TargetPosition(
                cube_location=CubeLocation(point=Point(x=250, y=250), angle=0),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
            TargetPosition(
                cube_location=CubeLocation(point=Point(x=120, y=170), angle=0),
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


async def main():
    print("1: motor_control()")
    await test_motor_1()
    print("2: motor_control_target()")
    await test_motor_2()
    print("3: motor_control_multiple_targets()")
    await test_motor_3()


asyncio.run(main())
