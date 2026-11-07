#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_configuration_v250.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import pytest

from toio.cube.api.configuration import (
    Configuration,
    RequestRemotePowerOff,
    ResetConfiguration,
    ResponseConfigurationReset,
    ResponseRemotePowerOff,
    ResponseSpeakerMuteSettings,
    SetSpeakerMute,
    SpeakerMute,
)


@pytest.mark.parametrize(
    "mute,expected",
    [
        (SpeakerMute.Unmute, b"\x33\x00\x00"),
        (SpeakerMute.MuteAll, b"\x33\x00\x01"),
        (SpeakerMute.MuteSystemOnly, b"\x33\x00\x02"),
    ],
)
def test_set_speaker_mute_bytes(mute, expected):
    assert bytes(SetSpeakerMute(mute)) == expected


def test_response_speaker_mute_settings():
    assert ResponseSpeakerMuteSettings(bytearray((0xB3, 0x00, 0x00))).result is True
    assert ResponseSpeakerMuteSettings(bytearray((0xB3, 0x00, 0x01))).result is False

    with pytest.raises(TypeError):
        ResponseSpeakerMuteSettings(bytearray((0x00, 0x00, 0x00)))


def test_configuration_dispatches_speaker_mute_response():
    payload = bytearray((0xB3, 0x00, 0x00))
    assert isinstance(Configuration.is_my_data(payload), ResponseSpeakerMuteSettings)


def test_reset_configuration_bytes():
    assert bytes(ResetConfiguration()) == b"\x0f\x00"


def test_response_configuration_reset():
    assert ResponseConfigurationReset(bytearray((0x8F, 0x00, 0x00))).result is True
    assert ResponseConfigurationReset(bytearray((0x8F, 0x00, 0x01))).result is False

    with pytest.raises(TypeError):
        ResponseConfigurationReset(bytearray((0x00, 0x00, 0x00)))


def test_configuration_dispatches_configuration_reset_response():
    payload = bytearray((0x8F, 0x00, 0x00))
    assert isinstance(Configuration.is_my_data(payload), ResponseConfigurationReset)


@pytest.mark.parametrize(
    "time_s,expected",
    [
        (0, b"\x34\x00\x00"),
        (10, b"\x34\x00\x0a"),
        # time_s is clipped to a single byte
        (300, b"\x34\x00\xff"),
    ],
)
def test_request_remote_power_off_bytes(time_s, expected):
    assert bytes(RequestRemotePowerOff(time_s)) == expected


def test_response_remote_power_off():
    assert ResponseRemotePowerOff(bytearray((0xB4, 0x00, 0x00))).result is True
    assert ResponseRemotePowerOff(bytearray((0xB4, 0x00, 0x01))).result is False

    with pytest.raises(TypeError):
        ResponseRemotePowerOff(bytearray((0x00, 0x00, 0x00)))


def test_configuration_dispatches_remote_power_off_response():
    payload = bytearray((0xB4, 0x00, 0x00))
    assert isinstance(Configuration.is_my_data(payload), ResponseRemotePowerOff)
