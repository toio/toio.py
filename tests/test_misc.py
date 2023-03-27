#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_misc.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import inspect
from logging import getLogger

from toio.standard_id import StandardIdCard
from toio.utility import clip

logger = getLogger(__name__)


def test_standard_id():
    for card in StandardIdCard:
        logger.info("%d: (%s)", card.value, card.name)


def test_clip():
    assert clip(10, -100, 100) == 10
    assert clip(-10, -100, 100) == -10
    assert clip(100, -100, 100) == 100
    assert clip(-100, -100, 100) == -100
    assert clip(101, -100, 100) == 100
    assert clip(-101, -100, 100) == -100


def test_simple_import():
    import toio.simple as simple_api

    assert inspect.isclass(simple_api.SimpleCube)
