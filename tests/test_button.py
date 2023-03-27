#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_button.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
from logging import getLogger

import pytest

from toio.cube import Button, ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


def button_handler(payload: bytearray):
    button_info = Button.is_my_data(payload)
    if button_info is not None:
        logger.info("notification: " + pprint.pformat(str(button_info)))


@pytest.mark.asyncio
async def test_button():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.button.register_notification_handler(button_handler)
    for i in range(15):
        button = await cube.api.button.read()
        logger.info("read: " + pprint.pformat(str(button)))
        await asyncio.sleep(1)
    await cube.api.button.unregister_notification_handler(button_handler)
    logger.info("** DISCONNECT")
    await cube.disconnect()
