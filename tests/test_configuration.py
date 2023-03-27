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

from toio.cube import Configuration, ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


def notification_handler(payload: bytearray):
    logger.debug(binascii.hexlify(payload, " "))
    configuration_info = Configuration.is_my_data(payload)
    if configuration_info is not None:
        logger.info("notification: " + pprint.pformat(str(configuration_info)))


@pytest.mark.asyncio
async def test_configuration():
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
    await cube.disconnect()
