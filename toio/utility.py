# -*- coding: utf-8 -*-
# ************************************************************
#
#     utility.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
General utility functions
"""

from typing import Any


def clip(x: Any, min_val: Any, max_val: Any):
    assert min_val < max_val
    if x < min_val:
        return min_val
    elif max_val < x:
        return max_val
    else:
        return x
