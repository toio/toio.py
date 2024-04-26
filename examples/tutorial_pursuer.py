#!/usr/bin/env python

import asyncio

from toio import *

green_cube_location = None
red_cube_arrived = True


async def pursuer():
    global green_cube_location
    global red_cube_arrived

    def id_notification_handler(payload: bytearray):
        global green_cube_location
        id_info = IdInformation.is_my_data(payload)
        if isinstance(id_info, PositionId):
            green_cube_location = id_info.center

    def motor_notification_handler(payload: bytearray):
        global red_cube_arrived
        motor_response = Motor.is_my_data(payload)
        if isinstance(motor_response, ResponseMotorControlTarget):
            print(motor_response)
            red_cube_arrived = True

    async with MultipleToioCoreCubes(2, ("red", "green")) as cubes:
        red = IndicatorParam(duration_ms=0, color=Color(r=255, g=0, b=0))
        green = IndicatorParam(duration_ms=0, color=Color(r=0, g=255, b=0))

        await asyncio.gather(
            cubes.green.api.indicator.turn_on(green),
            cubes.red.api.indicator.turn_on(red),
        )

        print("start")
        await cubes.green.api.id_information.register_notification_handler(
            id_notification_handler
        )
        await cubes.red.api.motor.register_notification_handler(
            motor_notification_handler
        )

        for _ in range(30):
            if green_cube_location is not None and red_cube_arrived:
                red_cube_arrived = False
                print("red cube: move to", str(green_cube_location))
                await cubes.red.api.motor.motor_control_target(
                    timeout=5,
                    movement_type=MovementType.Linear,
                    speed=Speed(
                        max=100,
                        speed_change_type=SpeedChangeType.AccelerationAndDeceleration,
                    ),
                    target=TargetPosition(
                        cube_location=green_cube_location,
                        rotation_option=RotationOption.AbsoluteOptimal,
                    ),
                )

            await asyncio.sleep(1)

        await cubes.red.api.motor.unregister_notification_handler(
            motor_notification_handler
        )
        await cubes.green.api.id_information.unregister_notification_handler(
            id_notification_handler
        )
        print("end")


asyncio.run(pursuer())
