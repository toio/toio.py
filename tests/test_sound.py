#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_sound.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import pprint
from logging import getLogger

import pytest

from toio.cube import MidiNote, Note, ToioCoreCube
from toio.scanner import BLEScanner

logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_sound():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    for n in Note:
        note = MidiNote(100, n, 255)
        logger.info("sound:" + pprint.pformat(str(note)))
        await cube.api.sound.play_midi(1, [note])
        await asyncio.sleep(0.2)
    logger.info("** DISCONNECT")
    await cube.disconnect()
