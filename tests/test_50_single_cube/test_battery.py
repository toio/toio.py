#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_battery.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
from logging import getLogger

import pytest

from toio.cube import Battery, ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


def battery_handler(payload: bytearray):
    battery_info = Battery.is_my_data(payload)
    if battery_info is not None:
        logger.info("notification: " + pprint.pformat(str(battery_info)))


@pytest.mark.asyncio
async def test_battery():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.battery.register_notification_handler(battery_handler)
    for i in range(15):
        battery = await cube.api.battery.read()
        logger.info("read: " + pprint.pformat(str(battery)))
        await asyncio.sleep(1)
    await cube.api.battery.unregister_notification_handler(battery_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()
