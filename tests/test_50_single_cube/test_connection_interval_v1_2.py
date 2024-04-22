#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_connection_interval_v1_2.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import binascii
import pprint
from logging import getLogger

import pytest

from toio.cube import Configuration, ToioCoreCube
from toio.cube.api.configuration import (
    ConnectionInterval,
    ResponseConnectionIntervalRequest,
    ResponseGettingCurrentConnectionInterval,
    ResponseGettingRequestedConnectionInterval,
)
from toio.scanner import BLEScanner

logger = getLogger(__name__)


def notification_handler(payload: bytearray):
    logger.debug(binascii.hexlify(payload, " "))
    configuration_info = Configuration.is_my_data(payload)
    if configuration_info is not None:
        if isinstance(configuration_info, ResponseConnectionIntervalRequest):
            logger.info(
                "request connection interval result: %s", configuration_info.result
            )
        elif isinstance(configuration_info, ResponseGettingCurrentConnectionInterval):
            logger.info(
                "current connection interval:%f (%s)",
                configuration_info.interval.value_ms,
                str(configuration_info.interval),
            )
        elif isinstance(configuration_info, ResponseGettingRequestedConnectionInterval):
            logger.info(
                "requested connection interval (min): %s",
                str(configuration_info.min_interval),
            )
            logger.info(
                "requested connection interval (max): %s",
                str(configuration_info.max_interval),
            )


@pytest.mark.asyncio
async def test_connection_interval_1():
    logger.info("** CONFIG: GET CURRENT CONNECTION INTERVAL")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube.create(device_list)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.get_current_connection_interval()
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_connection_interval_2():
    logger.info("** CONFIG: GET REQUESTED CONNECTION INTERVAL")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube.create(device_list)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.configuration.register_notification_handler(notification_handler)
    for i in range(5):
        await cube.api.configuration.get_requested_connection_interval()
        await asyncio.sleep(1)
    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()


@pytest.mark.asyncio
async def test_connection_interval_3():
    logger.info("** CONFIG: CHANGE CONNECTION INTERVAL")
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube.create(device_list)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    logger.info("-- request min:10, max:10")
    await cube.api.configuration.register_notification_handler(notification_handler)

    logger.info("-- request min:10, max:10")
    await cube.api.configuration.request_to_change_connection_interval(
        ConnectionInterval.from_ms(10), ConnectionInterval.from_ms(10)
    )
    await asyncio.sleep(1)
    await cube.api.configuration.get_requested_connection_interval()
    await asyncio.sleep(1)
    await cube.api.configuration.get_current_connection_interval()
    await asyncio.sleep(2)

    logger.info("-- request min:0xffff, max:80")
    await cube.api.configuration.request_to_change_connection_interval(
        0xFFFF, ConnectionInterval.from_ms(80)
    )
    await asyncio.sleep(1)
    await cube.api.configuration.get_requested_connection_interval()
    await asyncio.sleep(1)
    await cube.api.configuration.get_current_connection_interval()
    await asyncio.sleep(2)

    logger.info("-- request min:0x10, max:0xffff")
    await cube.api.configuration.request_to_change_connection_interval(
        ConnectionInterval.from_ms(10), 0xFFFF
    )
    await asyncio.sleep(1)
    await cube.api.configuration.get_requested_connection_interval()
    await asyncio.sleep(1)
    await cube.api.configuration.get_current_connection_interval()
    await asyncio.sleep(2)

    logger.info("-- request min:10, max:80")
    await cube.api.configuration.request_to_change_connection_interval(
        ConnectionInterval.from_ms(10), ConnectionInterval.from_ms(80)
    )
    await asyncio.sleep(1)
    await cube.api.configuration.get_requested_connection_interval()
    await asyncio.sleep(1)
    await cube.api.configuration.get_current_connection_interval()
    await asyncio.sleep(2)

    await cube.api.configuration.unregister_notification_handler(notification_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()
