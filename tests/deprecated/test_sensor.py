#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_sensor.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import binascii
import pprint
from logging import getLogger

import pytest

from toio.cube import (
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    Sensor,
    ToioCoreCube,
)
from toio.scanner import BLEScanner

logger = getLogger(__name__)


def sensor_handler(payload: bytearray):
    logger.debug(binascii.hexlify(payload, " "))
    sensor_info = Sensor.is_my_data(payload)
    if sensor_info is not None:
        logger.info("notification: " + pprint.pformat(str(sensor_info)))


@pytest.mark.asyncio
async def test_sensor():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.sensor.register_notification_handler(sensor_handler)
    for i in range(15):
        sensor = await cube.api.sensor.read()
        logger.info("read: " + pprint.pformat(str(sensor)))
        await asyncio.sleep(1)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_sensor_2():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.set_posture_angle_detection(
        PostureAngleDetectionType.Euler, 100, PostureAngleDetectionCondition.Always
    )
    await cube.api.sensor.register_notification_handler(sensor_handler)
    for i in range(15):
        sensor = await cube.api.sensor.read()
        logger.info("read: " + pprint.pformat(str(sensor)))
        await asyncio.sleep(1)
    await cube.api.sensor.unregister_notification_handler(sensor_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()
