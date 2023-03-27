# -*- coding: utf-8 -*-
# ************************************************************
#
#     logger.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from logging import (
    DEBUG,
    NOTSET,
    Handler,
    Logger,
    NullHandler,
    StreamHandler,
    getLogger,
)

TOIO_LOGGER_NAME = "ToioPyLogger"
TOIO_DEFAULT_LOG_LEVEL = DEBUG

toio_module_logger: Logger = getLogger(TOIO_LOGGER_NAME)
toio_module_handler: Handler = NullHandler()

toio_module_handler.setLevel(TOIO_DEFAULT_LOG_LEVEL)
toio_module_logger.setLevel(TOIO_DEFAULT_LOG_LEVEL)
toio_module_logger.addHandler(toio_module_handler)


def get_toio_logger(module_name: str, level: int = NOTSET) -> Logger:
    child_logger = getLogger(TOIO_LOGGER_NAME).getChild(module_name)
    child_logger.setLevel(level)
    child_handler = NullHandler()
    child_handler.setLevel(level)
    child_logger.addHandler(child_handler)
    return child_logger


def change_toio_log_level(level: int) -> None:
    global toio_module_logger
    global toio_module_handler
    toio_module_handler.setLevel(level)
    toio_module_logger.setLevel(level)


def output_toio_log(enable: bool) -> None:
    global toio_module_logger
    global toio_module_handler
    toio_module_logger.removeHandler(toio_module_handler)
    if enable:
        toio_module_handler = StreamHandler()
    else:
        toio_module_handler = NullHandler()
    toio_module_handler.setLevel(TOIO_DEFAULT_LOG_LEVEL)
    toio_module_logger.addHandler(toio_module_handler)
