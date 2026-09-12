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
from toio.cube.api.button import Button, ButtonInformation, ButtonState
from toio.cube.api.configuration import (
    Configuration,
    ResponseConfigurationReset,
    ResponseSpeakerMuteSettings,
    SpeakerMute,
)
from toio.cube.api.sound import MidiNote, Note
from toio.scanner import BLEScanner

logger = getLogger(__name__)

RESPONSE_TIMEOUT: float = 2.0


async def _wait_button_pressed(cube: ToioCoreCube) -> None:
    """Block until the operator holds down the cube function button."""
    pressed = asyncio.Event()

    def button_handler(payload):
        button_info = Button.is_my_data(payload)
        if isinstance(button_info, ButtonInformation):
            if button_info.state == ButtonState.PRESSED:
                pressed.set()
            else:
                pressed.clear()

    await cube.api.button.register_notification_handler(button_handler)
    try:
        logger.info(">> PLEASE HOLD THE CUBE BUTTON")
        await pressed.wait()
        logger.info(">> BUTTON DETECTED")
    finally:
        await cube.api.button.unregister_notification_handler(button_handler)


async def _send_while_button_pressed(cube: ToioCoreCube, response_type, send):
    """Send a savable configuration command while the button is held."""
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    async def notification_handler(payload):
        response = Configuration.is_my_data(payload)
        if isinstance(response, response_type) and not future.done():
            future.set_result(response)

    await cube.api.configuration.register_notification_handler(notification_handler)
    try:
        await _wait_button_pressed(cube)
        await send()
        return await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT)
    finally:
        await cube.api.configuration.unregister_notification_handler(
            notification_handler
        )


async def _play_note(cube: ToioCoreCube) -> None:
    await cube.api.sound.play_midi(
        repeat=1,
        midi_notes=[MidiNote(duration_ms=1000, note=Note.C4, volume=255)],
    )
    await asyncio.sleep(2)


@pytest.mark.asyncio
async def test_speaker_mute(interactive, confirm, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    try:
        logger.info("===== MUTE ALL TEST =====")
        response = await _send_while_button_pressed(
            cube,
            ResponseSpeakerMuteSettings,
            lambda: cube.api.configuration.set_speaker_mute(SpeakerMute.MuteAll),
        )
        assert response.result is True
        logger.info(">> PLAYING SOUND (should be SILENT)")
        await _play_note(cube)

        logger.info("===== UNMUTE TEST =====")
        response = await _send_while_button_pressed(
            cube,
            ResponseSpeakerMuteSettings,
            lambda: cube.api.configuration.set_speaker_mute(SpeakerMute.Unmute),
        )
        assert response.result is True
        logger.info(">> PLAYING SOUND (should be AUDIBLE)")
        await _play_note(cube)
    finally:
        logger.info("** DISCONNECTING")
        await cube.disconnect()
        logger.info("** DISCONNECTED")


@pytest.mark.asyncio
async def test_configuration_reset(interactive, confirm, get_result):
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    try:
        logger.info("===== CONFIGURATION RESET TEST =====")
        response = await _send_while_button_pressed(
            cube,
            ResponseConfigurationReset,
            cube.api.configuration.reset_configuration,
        )
        assert response.result is True
    finally:
        logger.info("** DISCONNECTING")
        await cube.disconnect()
        logger.info("** DISCONNECTED")
