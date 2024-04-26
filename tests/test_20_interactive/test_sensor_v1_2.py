#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_sensor_v1_2.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
from logging import getLogger

import pytest

from toio.cube import (
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    ToioCoreCube,
)
from toio.cube.api.button import Button, ButtonInformation, ButtonState
from toio.cube.api.sensor import (
    MotionDetectionData,
    Posture,
    PostureAngleEulerData,
    PostureAngleHighPrecisionEulerData,
    PostureAngleQuaternionsData,
    Sensor,
)
from toio.cube.api.sound import SoundId
from toio.scanner import BLEScanner

logger = getLogger(__name__)


BUTTON_PRESSED: bool = False


def button_handler(payload: bytearray):
    button = Button.is_my_data(payload)
    if isinstance(button, ButtonInformation):
        global BUTTON_PRESSED
        logger.info("** BUTTON STATE: %s", ButtonState(button.state).name)
        if button.state == ButtonState.PRESSED and not BUTTON_PRESSED:
            BUTTON_PRESSED = True


@pytest.mark.asyncio
async def test_sensor_1(interactive, confirm):
    global BUTTON_PRESSED
    BUTTON_PRESSED = False

    result = []
    posture = None
    conditions = {
        Posture.Top: {"axis": "yaw", "angle_list": list(range(-180, 180, 15))},
        Posture.Front: {"axis": "pitch", "angle_list": [90]},
        Posture.Rear: {"axis": "pitch", "angle_list": [-90]},
        Posture.Left: {"axis": "roll", "angle_list": [90]},
        Posture.Right: {"axis": "roll", "angle_list": [-90]},
        Posture.Bottom: {"axis": "yaw", "angle_list": list(range(-180, 180, 15))},
    }

    def get_total_number_of_conditions(conditions):
        condition_num = 0
        for value in conditions.values():
            condition_num += len(value["angle_list"])
        return condition_num

    def get_remained_axes_name(conditions):
        axes = []
        for key, value in conditions.items():
            if len(value["angle_list"]):
                axes.append(Posture(key).name)
        return ",".join(axes)

    total_conditions = get_total_number_of_conditions(conditions)
    current_conditions = get_total_number_of_conditions(conditions)

    async def sensor_handler(payload: bytearray):
        nonlocal result
        nonlocal posture
        nonlocal conditions
        nonlocal current_conditions

        tolerance = 5.0

        sensor_info = Sensor.is_my_data(payload)
        if isinstance(sensor_info, MotionDetectionData):
            posture = sensor_info.posture
        elif isinstance(sensor_info, PostureAngleEulerData):
            if (
                abs(sensor_info.yaw) < tolerance
                and abs(sensor_info.pitch) < tolerance
                and abs(sensor_info.roll) < tolerance
            ):
                await cube.api.sound.play_sound_effect(SoundId.Enter, volume=255)

            if posture:
                axis = conditions[posture]["axis"]
                for target_angle in conditions[posture]["angle_list"]:
                    angle = sensor_info.__getattribute__(axis)
                    if abs(target_angle - angle) < tolerance:
                        conditions[posture]["angle_list"].remove(target_angle)
                        current_conditions = get_total_number_of_conditions(conditions)
                        logger.info(
                            "conditions met: %d/%d (%f%%) %s:%s:%s",
                            current_conditions,
                            total_conditions,
                            ((total_conditions - current_conditions) / total_conditions)
                            * 100,
                            Posture(posture).name,
                            axis,
                            conditions[posture]["angle_list"],
                        )

    logger.info("** EULER NOTIFICATION")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.Euler,
        50,
        PostureAngleDetectionCondition.Always,
    )
    await cube.api.sensor.register_notification_handler(sensor_handler)
    await cube.api.button.register_notification_handler(button_handler)
    await cube.api.sensor.request_motion_information()
    while current_conditions > 0 and not BUTTON_PRESSED:
        logger.info(
            "conditions met: %d/%d (%f%%) %s",
            current_conditions,
            total_conditions,
            ((total_conditions - current_conditions) / total_conditions) * 100,
            get_remained_axes_name(conditions),
        )
        await asyncio.sleep(1)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
    logger.info(
        "conditions met: %d/%d (%f%%) %s",
        current_conditions,
        total_conditions,
        ((total_conditions - current_conditions) / total_conditions) * 100,
        get_remained_axes_name(conditions),
    )
    logger.info("\n%s", pprint.pformat(conditions))
    assert current_conditions == 0
    assert BUTTON_PRESSED == False


@pytest.mark.asyncio
async def test_sensor_2(interactive, confirm):
    global BUTTON_PRESSED
    BUTTON_PRESSED = False

    result = []
    posture = None
    conditions = {
        Posture.Top: {"axis": "yaw", "angle_list": list(range(-180, 180, 15))},
        Posture.Front: {"axis": "pitch", "angle_list": [90]},
        Posture.Rear: {"axis": "pitch", "angle_list": [-90]},
        Posture.Left: {"axis": "roll", "angle_list": [90]},
        Posture.Right: {"axis": "roll", "angle_list": [-90]},
        Posture.Bottom: {"axis": "yaw", "angle_list": list(range(-180, 180, 15))},
    }

    def get_total_number_of_conditions(conditions):
        condition_num = 0
        for value in conditions.values():
            condition_num += len(value["angle_list"])
        return condition_num

    def get_remained_axes_name(conditions):
        axes = []
        for key, value in conditions.items():
            if len(value["angle_list"]):
                axes.append(Posture(key).name)
        return ",".join(axes)

    total_conditions = get_total_number_of_conditions(conditions)
    current_conditions = get_total_number_of_conditions(conditions)

    async def sensor_handler(payload: bytearray):
        nonlocal result
        nonlocal posture
        nonlocal conditions
        nonlocal current_conditions

        tolerance = 5.0

        sensor_info = Sensor.is_my_data(payload)
        if isinstance(sensor_info, MotionDetectionData):
            posture = sensor_info.posture
        elif isinstance(sensor_info, PostureAngleHighPrecisionEulerData):
            if (
                abs(sensor_info.yaw) < tolerance
                and abs(sensor_info.pitch) < tolerance
                and abs(sensor_info.roll) < tolerance
            ):
                await cube.api.sound.play_sound_effect(SoundId.Enter, volume=255)
            if posture:
                axis = conditions[posture]["axis"]
                for target_angle in conditions[posture]["angle_list"]:
                    angle = sensor_info.__getattribute__(axis)
                    if abs(target_angle - angle) < tolerance:
                        conditions[posture]["angle_list"].remove(target_angle)
                        current_conditions = get_total_number_of_conditions(conditions)
                        logger.info(
                            "conditions met: %d/%d (%f%%) %s:%s:%s",
                            current_conditions,
                            total_conditions,
                            ((total_conditions - current_conditions) / total_conditions)
                            * 100,
                            Posture(posture).name,
                            axis,
                            conditions[posture]["angle_list"],
                        )

    logger.info("** HIGH PRECISION EULER NOTIFICATION")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.HighPrecisionEuler,
        50,
        PostureAngleDetectionCondition.Always,
    )
    await cube.api.sensor.register_notification_handler(sensor_handler)
    await cube.api.button.register_notification_handler(button_handler)
    await cube.api.sensor.request_motion_information()
    while current_conditions > 0 and not BUTTON_PRESSED:
        logger.info(
            "conditions met: %d/%d (%f%%) %s",
            current_conditions,
            total_conditions,
            ((total_conditions - current_conditions) / total_conditions) * 100,
            get_remained_axes_name(conditions),
        )
        await asyncio.sleep(1)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
    logger.info(
        "conditions met: %d/%d (%f%%) %s",
        current_conditions,
        total_conditions,
        ((total_conditions - current_conditions) / total_conditions) * 100,
        get_remained_axes_name(conditions),
    )
    logger.info("\n%s", pprint.pformat(conditions))
    assert current_conditions == 0
    assert BUTTON_PRESSED == False


@pytest.mark.asyncio
async def test_sensor_3(interactive, confirm):
    global BUTTON_PRESSED
    BUTTON_PRESSED = False

    result = []
    posture = None
    conditions = {
        "x": [
            (1.0, 0, 0, 0),  # 0
            (0.9239, 0.3827, 0, 0),  # 45
            (0.7071, 0.7071, 0, 0),  # 90
            (0.3827, 0.9239, 0, 0),  # 135
            (0, 1.0, 0, 0),  # 180
            (-0.3827, 0.9239, 0, 0),  # 225
            (-0.7071, 0.7071, 0, 0),  # 270
            (-0.9239, 0.3827, 0, 0),  # 315
        ],
        "y": [
            (1.0, 0, 0, 0),  # 0
            (0.9239, 0, 0.3827, 0),  # 45
            (0.7071, 0, 0.7071, 0),  # 90
            (0.3827, 0, 0.9239, 0),  # 135
            (0, 0, 1.0, 0),  # 180
            (-0.3827, 0, 0.9239, 0),  # 225
            (-0.7071, 0, 0.7071, 0),  # 270
            (-0.9239, 0, 0.3827, 0),  # 315
        ],
        "z": [
            (1.0, 0, 0, 0),  # 0
            (0.9239, 0, 0, 0.3827),  # 45
            (0.7071, 0, 0, 0.7071),  # 90
            (0.3827, 0, 0, 0.9239),  # 135
            (0, 0, 0, 1.0),  # 180
            (-0.3827, 0, 0, 0.9239),  # 225
            (-0.7071, 0, 0, 0.7071),  # 270
            (-0.9239, 0, 0, 0.3827),  # 315
        ],
    }

    def get_total_number_of_conditions(conditions):
        condition_num = 0
        for value in conditions.values():
            condition_num += len(value)
        return condition_num

    def get_remained_axes_name(conditions):
        axes = []
        for key, value in conditions.items():
            if len(value):
                axes.append(key)
        return ",".join(axes)

    total_conditions = get_total_number_of_conditions(conditions)
    current_conditions = get_total_number_of_conditions(conditions)

    async def sensor_handler(payload: bytearray):
        nonlocal result
        nonlocal posture
        nonlocal conditions
        nonlocal current_conditions

        tolerance = 0.2

        sensor_info = Sensor.is_my_data(payload)
        if isinstance(sensor_info, PostureAngleQuaternionsData):
            w, x, y, z = sensor_info.w, sensor_info.x, sensor_info.y, sensor_info.z
            logger.info(
                "w:%f x:%f y:%f z:%f %d/%d (%f%%) %s",
                w,
                x,
                y,
                z,
                current_conditions,
                total_conditions,
                ((total_conditions - current_conditions) / total_conditions) * 100,
                get_remained_axes_name(conditions),
            )
            if (
                abs(1.0 - w) <= tolerance
                and abs(0 - x) <= tolerance
                and abs(0 - y) <= tolerance
                and abs(0 - z) <= tolerance
            ):
                await cube.api.sound.play_sound_effect(SoundId.Enter, volume=255)

            for key, quaternions in conditions.items():
                for target_value in quaternions:
                    target_w, target_x, target_y, target_z = target_value
                    if (
                        abs(target_w - w) <= tolerance
                        and abs(target_x - x) <= tolerance
                        and abs(target_y - y) <= tolerance
                        and abs(target_z - z) <= tolerance
                    ):
                        conditions[key].remove(target_value)
                        current_conditions = get_total_number_of_conditions(conditions)
                        logger.info(
                            "conditions met: %d/%d (%f%%) %s:%s",
                            current_conditions,
                            total_conditions,
                            ((total_conditions - current_conditions) / total_conditions)
                            * 100,
                            key,
                            conditions[key],
                        )

    logger.info("** QUATERNION NOTIFICATION")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.Quaternions,
        50,
        PostureAngleDetectionCondition.Always,
    )
    await cube.api.sensor.register_notification_handler(sensor_handler)
    await cube.api.button.register_notification_handler(button_handler)
    while current_conditions > 0 and not BUTTON_PRESSED:
        await asyncio.sleep(0.1)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
    logger.info(
        "conditions met: %d/%d (%f%%)",
        current_conditions,
        total_conditions,
        ((total_conditions - current_conditions) / total_conditions) * 100,
    )
    logger.info("\n%s", pprint.pformat(conditions))
    assert current_conditions == 0
    assert BUTTON_PRESSED == False


@pytest.mark.asyncio
async def test_sensor_4():
    global BUTTON_PRESSED
    BUTTON_PRESSED = False

    result = []
    posture = None
    conditions = {
        "horizontal": [True, False],
        "collision": [True, False],
        "double_tap": [True, False],
        "posture": [1, 2, 3, 4, 5, 6],
        "shake": list(range(10)),
    }

    def get_number_of_conditions_remaining(conditions):
        condition_num = 0
        for _, value in conditions.items():
            condition_num += len(value)
        return condition_num

    total_conditions = get_number_of_conditions_remaining(conditions)
    current_conditions = get_number_of_conditions_remaining(conditions)

    async def sensor_handler(payload: bytearray):
        nonlocal result
        nonlocal posture
        nonlocal conditions
        nonlocal current_conditions

        sensor_info = Sensor.is_my_data(payload)
        if isinstance(sensor_info, MotionDetectionData):
            if sensor_info.horizontal in conditions["horizontal"]:
                conditions["horizontal"].remove(sensor_info.horizontal)
            if sensor_info.collision in conditions["collision"]:
                conditions["collision"].remove(sensor_info.collision)
            if sensor_info.double_tap in conditions["double_tap"]:
                conditions["double_tap"].remove(sensor_info.double_tap)
            if sensor_info.posture in conditions["posture"]:
                conditions["posture"].remove(sensor_info.posture)
            if sensor_info.shake in conditions["shake"]:
                conditions["shake"].remove(sensor_info.shake)
            current_conditions = get_number_of_conditions_remaining(conditions)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.sensor.register_notification_handler(sensor_handler)
    await cube.api.button.register_notification_handler(button_handler)
    while current_conditions > 0 and not BUTTON_PRESSED:
        logger.info("read: %s:%d", str(conditions), current_conditions)
        await asyncio.sleep(0.1)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
    assert current_conditions == 0
    assert BUTTON_PRESSED == False


@pytest.mark.asyncio
async def test_sensor_5():
    logger.info("** HIGH PRECISION EULER READ")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.HighPrecisionEuler,
        50,
        PostureAngleDetectionCondition.Always,
    )
    read_test = 10
    while read_test > 0:
        sensor_info = await cube.api.sensor.read()
        if isinstance(sensor_info, PostureAngleHighPrecisionEulerData):
            if read_test > 0:
                logger.info("read api test (euler): %s", sensor_info)
                read_test -= 1
        await asyncio.sleep(0.1)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_sensor_6():
    logger.info("** QUATERNION READ")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.Quaternions,
        50,
        PostureAngleDetectionCondition.Always,
    )
    read_test = 10
    while read_test > 0:
        sensor_info = await cube.api.sensor.read()
        if isinstance(sensor_info, PostureAngleQuaternionsData):
            if read_test > 0:
                logger.info("read api test (quaternion): %s", sensor_info)
                read_test -= 1
        await asyncio.sleep(0.1)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_sensor_7():
    logger.info("** MOTION DETECTION DATA READ")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    read_test = 10
    while read_test > 0:
        sensor_info = await cube.api.sensor.read()
        if isinstance(sensor_info, MotionDetectionData):
            if read_test > 0:
                logger.info("read api test (motion detection data): %s", sensor_info)
                read_test -= 1
        await asyncio.sleep(0.1)
    logger.info("** DISCONNECT")
    await cube.disconnect()
