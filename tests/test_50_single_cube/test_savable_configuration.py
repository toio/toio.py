#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_savable_configuration.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from logging import getLogger

import pytest

from toio.cube import ToioCoreCube
from toio.cube.api.configuration import (
    Configuration,
    ResponseSpeakerMuteSettings,
    SpeakerMute,
)
from toio.scanner import BLEScanner

logger = getLogger(__name__)

RESPONSE_TIMEOUT: float = 5.0


async def _wait_response(cube: ToioCoreCube, response_type, send):
    """Send a savable configuration command and wait for its response."""
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    async def notification_handler(payload):
        response = Configuration.is_my_data(payload)
        if isinstance(response, response_type) and not future.done():
            future.set_result(response)

    await cube.api.configuration.register_notification_handler(notification_handler)
    try:
        await send()
        return await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT)
    finally:
        await cube.api.configuration.unregister_notification_handler(
            notification_handler
        )


@pytest.mark.asyncio
async def test_speaker_mute_is_rejected_without_button():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    try:
        # Savable configuration is only writable while the function button is
        # held, so the cube is expected to reject this request.
        response = await _wait_response(
            cube,
            ResponseSpeakerMuteSettings,
            lambda: cube.api.configuration.set_speaker_mute(SpeakerMute.MuteAll),
        )
        assert response.result is False
    finally:
        logger.info("** DISCONNECTING")
        await cube.disconnect()
