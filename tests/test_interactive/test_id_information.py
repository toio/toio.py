#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_id_information.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
from dataclasses import dataclass
from logging import getLogger

import pytest
from typing_extensions import List

from toio.cube import ToioCoreCube
from toio.cube.api.button import Button, ButtonInformation, ButtonState
from toio.cube.api.id_information import (
    IdInformation,
    IdInformationResponseType,
    PositionId,
    StandardId,
)
from toio.position import CubeLocation
from toio.scanner import BLEScanner
from toio.standard_id import StandardIdCard

logger = getLogger(__name__)


@dataclass
class TargetArea:
    x: int
    y: int
    width: int
    height: int
    angle: int

    def contains(self, pos: CubeLocation):
        if (
            (self.x <= pos.point.x <= (self.x + self.width))
            and (self.y <= pos.point.y <= (self.y + self.height))
            and abs(self.angle - (pos.angle % 360)) < 5
        ):
            return True
        else:
            return False


TARGET_AREA: List[TargetArea] = []
TARGET_CARD: List[StandardIdCard] = []


def id_information_handler(payload: bytearray):
    global TARGET_AREA
    global TARGET_CARD
    id_info = IdInformation.is_my_data(payload)
    if isinstance(id_info, PositionId):
        logger.info(
            "(%d, %d) %d: %d",
            id_info.center.point.x,
            id_info.center.point.y,
            id_info.center.angle,
            len(TARGET_AREA),
        )
        for area in TARGET_AREA:
            if area.contains(id_info.center):
                logger.info("CONTAINS")
                TARGET_AREA.remove(area)
    elif isinstance(id_info, StandardId):
        logger.info("%08x", id_info.value)
        for card in TARGET_CARD:
            if card == id_info.value:
                logger.info("CHECKED")
                TARGET_CARD.remove(card)


BUTTON_PRESSED = False


def button_handler(payload: bytearray):
    button = Button.is_my_data(payload)
    if isinstance(button, ButtonInformation):
        global BUTTON_PRESSED
        if button.state == ButtonState.PRESSED and not BUTTON_PRESSED:
            BUTTON_PRESSED = True
            logger.info("EXIT")


def reset_state():
    global BUTTON_PRESSED
    BUTTON_PRESSED = False


@pytest.mark.asyncio
async def test_id_information_1():
    reset_state()

    global TARGET_AREA
    TARGET_AREA = [
        TargetArea(98, 142, 43, 43, 0),
        TargetArea(356, 142, 43, 43, 90),
        TargetArea(356, 314, 43, 43, 180),
        TargetArea(98, 314, 43, 43, 270),
    ]

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    logger.info("** CONNECTING...")
    await cube.connect()
    logger.info("** CONNECTED")
    await cube.api.id_information.register_notification_handler(id_information_handler)
    await cube.api.button.register_notification_handler(button_handler)
    while not BUTTON_PRESSED and len(TARGET_AREA) > 0:
        await asyncio.sleep(0.1)
    await cube.api.button.unregister_notification_handler(button_handler)
    await cube.api.id_information.unregister_notification_handler(
        id_information_handler
    )
    logger.info("** TEST COMPLETE")
    logger.info("** DISCONNECTING")
    await cube.disconnect()
    logger.info("** DISCONNECTED")
    assert len(TARGET_AREA) == 0
    assert BUTTON_PRESSED == False


@pytest.mark.asyncio
async def test_id_information_2():
    reset_state()

    global TARGET_CARD

    TARGET_CARD = [
        StandardIdCard.NUMBER_0,
        StandardIdCard.ALPHABET_E,
    ]

    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    async with ToioCoreCube(device_list[0].interface) as cube:
        logger.info("** CONNECTED")
        await cube.api.id_information.register_notification_handler(
            id_information_handler
        )
        await cube.api.button.register_notification_handler(button_handler)
        logger.info("===== touch the standard id card '0' and 'E'")
        while not BUTTON_PRESSED and len(TARGET_CARD) > 0:
            await asyncio.sleep(0.1)
        await cube.api.button.unregister_notification_handler(button_handler)
        await cube.api.id_information.unregister_notification_handler(
            id_information_handler
        )
        logger.info("** TEST COMPLETE")
        logger.info("** DISCONNECTING")
    logger.info("** DISCONNECTED")
    assert len(TARGET_CARD) == 0
    assert BUTTON_PRESSED == False
