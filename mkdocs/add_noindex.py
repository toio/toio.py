#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     add_noindex.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import sys
from logging import (
    DEBUG,
    NOTSET,
    Formatter,
    NullHandler,
    StreamHandler,
    getLogger,
)

logger = getLogger(__name__)
if __name__ == "__main__":
    default_log_level = DEBUG
    handler = StreamHandler()
    handler.setLevel(default_log_level)
    formatter = Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(default_log_level)
else:
    default_log_level = NOTSET
    handler = NullHandler()
logger.addHandler(handler)


def add_noindex(filename: str):
    logger.info("Add :noindex: to %s", filename)
    file_data = []
    with open(filename, "r") as rfh:
        file_data = rfh.readlines()
    with open(filename, "w") as wfh:
        for line in file_data:
            wfh.write(line)
            if ".. automodule::" in line:
                wfh.write("   :noindex:\n")


def main(argv):

    if len(argv) >= 2:
        for filename in argv[1:]:
            add_noindex(filename)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
