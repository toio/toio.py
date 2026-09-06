#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_sensor.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import struct

import toio
import toio.cube
from toio.cube.api.sensor import (
    PostureAngleEulerData,
    PostureAngleHighPrecisionEulerData,
    PostureAngleQuaternionsData,
    PostureDataType,
    Sensor,
)

POSTURE_ANGLE_PAYLOAD_ID = 0x03


def euler_payload() -> bytearray:
    return bytearray(
        struct.pack("<BBhhh", POSTURE_ANGLE_PAYLOAD_ID, PostureDataType.Euler, 1, 2, 3)
    )


def quaternions_payload() -> bytearray:
    return bytearray(
        struct.pack(
            "<BBffff",
            POSTURE_ANGLE_PAYLOAD_ID,
            PostureDataType.Quaternions,
            1.0,
            2.0,
            3.0,
            4.0,
        )
    )


def high_precision_euler_payload() -> bytearray:
    return bytearray(
        struct.pack(
            "<BBfff",
            POSTURE_ANGLE_PAYLOAD_ID,
            PostureDataType.HighPrecisionEuler,
            1.0,
            2.0,
            3.0,
        )
    )


def test_posture_angle_is_myself_is_exclusive():
    payloads = {
        PostureAngleEulerData: euler_payload(),
        PostureAngleQuaternionsData: quaternions_payload(),
        PostureAngleHighPrecisionEulerData: high_precision_euler_payload(),
    }
    for owner, payload in payloads.items():
        for candidate in payloads:
            assert candidate.is_myself(payload) is (candidate is owner)


def test_sensor_dispatches_posture_angle_payloads():
    assert isinstance(Sensor.is_my_data(euler_payload()), PostureAngleEulerData)
    assert isinstance(
        Sensor.is_my_data(quaternions_payload()), PostureAngleQuaternionsData
    )
    assert isinstance(
        Sensor.is_my_data(high_precision_euler_payload()),
        PostureAngleHighPrecisionEulerData,
    )


def test_posture_angle_high_precision_euler_data_is_exported():
    assert "PostureAngleHighPrecisionEulerData" in toio.__all__
    assert "PostureAngleHighPrecisionEulerData" in toio.cube.__all__
    assert (
        toio.PostureAngleHighPrecisionEulerData
        is toio.cube.PostureAngleHighPrecisionEulerData
    )
