#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_configuration.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import binascii
import pprint
from logging import getLogger

import pytest
from typing_extensions import Any, Tuple, Union

from toio.cube import Configuration, ToioCoreCube
from toio.cube.api.configuration import (
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
from toio.scanner import BLEScanner

logger = getLogger(__name__)

LAST_CONFIGURATION_NOTIFICATION: Tuple[str, Any] = ("", None)


def notification_handler(payload: bytearray):
    global LAST_CONFIGURATION_NOTIFICATION
    logger.debug(binascii.hexlify(payload, " "))
    configuration_info = Configuration.is_my_data(payload)
    if configuration_info is not None:
        logger.info("notification: " + pprint.pformat(str(configuration_info)))
    if isinstance(configuration_info, ProtocolVersion):
        LAST_CONFIGURATION_NOTIFICATION = ("ProtocolVersion", configuration_info)
    elif isinstance(configuration_info, ResponseIdNotificationSettings):
        LAST_CONFIGURATION_NOTIFICATION = (
            "ResponseIdNotificationSettings",
            configuration_info,
        )
    elif isinstance(configuration_info, ResponseIdMissedNotificationSettings):
        LAST_CONFIGURATION_NOTIFICATION = (
            "ResponseIdMissedNotificationSettings",
            configuration_info,
        )
    elif isinstance(configuration_info, ResponseMagneticSensorSettings):
        LAST_CONFIGURATION_NOTIFICATION = (
            "ResponseMagneticSensorSettings",
            configuration_info,
        )
    elif isinstance(
        configuration_info, ResponseMotorSpeedInformationAcquisitionSettings
    ):
        LAST_CONFIGURATION_NOTIFICATION = (
            "ResponseMotorSpeedInformationAcquisitionSettings",
            configuration_info,
        )
    elif isinstance(configuration_info, ResponsePostureAngleDetectionSettings):
        LAST_CONFIGURATION_NOTIFICATION = (
            "ResponsePostureAngleDetectionSettings",
            configuration_info,
        )


@pytest.mark.asyncio
async def test_configuration_1():
    logger.info("** CONFIG: REQUEST PROTOCOL VERSION")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.request_protocol_version()
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ProtocolVersion"
    assert isinstance(instance, ProtocolVersion)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()


@pytest.mark.asyncio
async def test_configuration_2():
    logger.info("** CONFIG: ID NOTIFICATION SETTINGS")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.set_id_notification(
            100, NotificationCondition.Always
        )
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ResponseIdNotificationSettings"
    assert isinstance(instance, ResponseIdNotificationSettings)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()


@pytest.mark.asyncio
async def test_configuration_3():
    logger.info("** CONFIG: ID MISSED NOTIFICATION SETTINGS")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.set_id_missed_notification(100)
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ResponseIdMissedNotificationSettings"
    assert isinstance(instance, ResponseIdMissedNotificationSettings)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()


@pytest.mark.asyncio
async def test_configuration_4():
    logger.info("** CONFIG: MAGNETIC SENSOR SETTINGS")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.set_magnetic_sensor(
            MagneticSensorFunction.MagneticForce, 100, MagneticSensorCondition.Always
        )
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ResponseMagneticSensorSettings"
    assert isinstance(instance, ResponseMagneticSensorSettings)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()


@pytest.mark.asyncio
async def test_configuration_5():
    logger.info("** CONFIG: MOTOR SPEED INFORMATION ACQUISITION SETTINGS")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.set_motor_speed_information_acquisition(
            MotorSpeedInformationAcquisitionState.Enable
        )
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ResponseMotorSpeedInformationAcquisitionSettings"
    assert isinstance(instance, ResponseMotorSpeedInformationAcquisitionSettings)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()


@pytest.mark.asyncio
async def test_configuration_6():
    logger.info("** CONFIG: POSTURE ANGLE DETECTION SETTINGS")
    global LAST_CONFIGURATION_NOTIFICATION
    LAST_CONFIGURATION_NOTIFICATION = ("**NO_NOTIFICATION**", None)

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.set_posture_angle_detection(
            PostureAngleDetectionType.HighPrecisionEuler,
            100,
            PostureAngleDetectionCondition.ChangeDetection.Always,
        )
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")

    logger.info("** CHECK NOTIFICATION TYPE")
    (name, instance) = LAST_CONFIGURATION_NOTIFICATION
    assert name == "ResponsePostureAngleDetectionSettings"
    assert isinstance(instance, ResponsePostureAngleDetectionSettings)
    logger.info("%s:%s", name, instance)
    await cube.disconnect()
