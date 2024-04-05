# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/scanner/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from typing_extensions import Tuple

from .ble import UniversalBleScanner

BLEScanner = UniversalBleScanner()

__all__: Tuple[str, ...] = ("BLEScanner",)
