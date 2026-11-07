#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_indicator_v250.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pytest

from toio.cube.api.indicator import Color, SmoothFlashing


def test_smooth_flashing_bytes():
    command = SmoothFlashing(5, 1000, Color(r=0x00, g=0xFF, b=0x40))
    # 0x70, repeat, id count, id, cycle (10ms unit), r, g, b
    assert bytes(command) == b"\x70\x05\x01\x01\x64\x00\xff\x40"


@pytest.mark.parametrize(
    "repeat,cycle_ms,expected_repeat,expected_cycle",
    [
        # 0 repeats means "flash forever"
        (0, 0, 0x00, 0x00),
        (300, 1000000, 0xFF, 0xFF),
    ],
)
def test_smooth_flashing_clips_arguments(
    repeat, cycle_ms, expected_repeat, expected_cycle
):
    payload = bytes(SmoothFlashing(repeat, cycle_ms, Color(r=0, g=0, b=0)))
    assert payload[1] == expected_repeat
    assert payload[4] == expected_cycle
