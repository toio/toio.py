#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_notification_handler_v1_2.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import binascii
import pprint
import pytest
from logging import getLogger
from typing_extensions import Dict
from toio.cube.api.button import Button, ButtonInformation, ButtonState
from toio.cube.api.indicator import IndicatorParam, Color
from toio.cube.api.sensor import Sensor, MotionDetectionData, Posture
from toio.cube import ToioCoreCube, NotificationHandlerInfo
from toio.scanner import BLEScanner

logger = getLogger(__name__)

POSTURE_COLOR: Dict[Posture, Color] = {
    Posture.Top: Color(0x00, 0x00, 0xFF),
    Posture.Rear: Color(0x00, 0xFF, 0x00),
    Posture.Left: Color(0xFF, 0x00, 0x00),
    Posture.Front: Color(0x00, 0xFF, 0xFF),
    Posture.Right: Color(0xFF, 0x00, 0xFF),
    Posture.Bottom: Color(0xFF, 0xFF, 0x00),
}

USER_DATA: str = "hello world"


async def async_sensor_handler_with_info(
    payload: bytearray, info: NotificationHandlerInfo
):
    notified_cube: ToioCoreCube = info.get_notified_cube()
    logger.info("indicator turn on: %s", notified_cube.name)
    sensor_info = Sensor.is_my_data(payload)
    if isinstance(sensor_info, MotionDetectionData):
        color = POSTURE_COLOR.get(sensor_info.posture)
        if color is not None:
            await notified_cube.api.indicator.turn_on(
                IndicatorParam(duration_ms=0, color=color)
            )


async def async_sensor_handler(payload: bytearray):
    logger.debug(binascii.hexlify(payload, " "))
    sensor_info = Sensor.is_my_data(payload)
    if sensor_info is not None:
        logger.info("notification: " + pprint.pformat(str(sensor_info)))


BUTTON_PRESSED: bool = False


def button_handler(payload: bytearray):
    global BUTTON_PRESSED
    button_info = Button.is_my_data(payload)
    if button_info is not None:
        if isinstance(button_info, ButtonInformation):
            if button_info.state == ButtonState.PRESSED and not BUTTON_PRESSED:
                logger.info("button pressed")
                BUTTON_PRESSED = True


def button_handler_with_info(payload: bytearray, info: NotificationHandlerInfo):
    notified_cube: ToioCoreCube = info.get_notified_cube()
    button_info = Button.is_my_data(payload)
    assert info.misc == USER_DATA
    if button_info is not None:
        if isinstance(button_info, ButtonInformation):
            logger.info("device:%s", info.device)
            logger.info("interface:%s", info.interface)
            logger.info("is_async:%s", info.is_async)
            logger.info("num_of_args:%s", info.num_of_args)
            logger.info(
                "button status:(%s) %s, %s, %s",
                notified_cube.name,
                info.misc,
                button_info.state,
                BUTTON_PRESSED,
            )


@pytest.mark.asyncio
async def test_notification_1():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface, device_list[0].name)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    sensor = await cube.api.sensor.read()
    logger.info("read: " + pprint.pformat(str(sensor)))
    await cube.api.sensor.register_notification_handler(async_sensor_handler_with_info)
    await cube.api.sensor.register_notification_handler(async_sensor_handler)
    await cube.api.button.register_notification_handler(
        button_handler_with_info, USER_DATA
    )
    await cube.api.button.register_notification_handler(button_handler)
    while not BUTTON_PRESSED:
        sensor = await cube.api.sensor.read()
        logger.info("read: " + pprint.pformat(str(sensor)))
        await asyncio.sleep(0.2)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.button.unregister_notification_handler(button_handler_with_info)
    await cube.api.sensor.unregister_notification_handler(async_sensor_handler)
    await cube.api.sensor.unregister_notification_handler(
        async_sensor_handler_with_info
    )
    logger.info("** DISCONNECT")
    await cube.disconnect()
