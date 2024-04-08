# -*- coding: utf-8 -*-
# ************************************************************
#
#     conftest.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

import os
import time
from logging import getLogger

import pytest
from colorama import Back, Fore, Style, init

logger = getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
def wait():
    time.sleep(2)


@pytest.fixture(scope="session", autouse=True)
def setup(pytestconfig):
    init()
    capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")

    logger.info(
        Fore.RED
        + "***** GENERATE CONFIGURATION FILE: _cubes.py *****"
        + Style.RESET_ALL
    )
    logger.info(
        "** This test requires a file '_cubes.py' that describes the cube to be used."
    )
    logger.info("** '_cube.py' is generated automatically.")
    logger.info("** To generate this, you turn on 2 cubes.")
    capmanager.suspend_global_capture(in_=True)
    yn = input(
        Fore.YELLOW
        + "Press Enter key when ready (If you don't need to generate, type 's' and Enter)"
        + Style.RESET_ALL
    )
    capmanager.resume_global_capture()
    logger.info("%s", yn)
    if yn.lower() != "s":
        logger.info("** GENERATE _cubes.py")
        result = os.system("python ./make_cube_list.py _cubes.py")
        if result:
            logger.info(
                Fore.RED
                + "** 2 cubes are not found. _cubes.py is not updated"
                + Style.RESET_ALL
            )
    else:
        logger.info(Fore.YELLOW + "** skip to generate _cubes.py" + Style.RESET_ALL)
    logger.info("** cubes used in this test:")
    with open("_cubes.py", "r") as rf:
        logger.info("\n" + rf.read())


@pytest.fixture(scope="function")
def confirm(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")
    capmanager.suspend_global_capture(in_=True)
    input(Fore.YELLOW + "\nPress Enter key when ready" + Style.RESET_ALL)
    capmanager.resume_global_capture()
    logger.info("start")


@pytest.fixture(scope="function")
def post_confirm(pytestconfig):
    yield  # At this point all the tests with this fixture are run
    capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")
    capmanager.suspend_global_capture(in_=True)
    input(Fore.YELLOW + "\nPress Enter key when ready" + Style.RESET_ALL)
    capmanager.resume_global_capture()


@pytest.fixture(scope="function")
def get_result(pytestconfig):
    logger.info(
        Fore.RED
        + "** You must check for yourself whether this test is a success or failure and enter the result **"
        + Style.RESET_ALL
    )
    yield  # At this point all the tests with this fixture are run
    capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")
    capmanager.suspend_global_capture(in_=True)
    yn = input(
        Fore.YELLOW
        + "\nIf this test fails, type 'N' and Enter. Otherwise, press Enter only"
        + Style.RESET_ALL
    )
    logger.info("%s", yn)
    capmanager.resume_global_capture()
    assert yn.lower() != "n"


@pytest.fixture(scope="function")
def interactive():
    logger.info(
        Fore.YELLOW
        + "***** INTERACTIVE TEST (MANUAL CUBE OPERATION REQUIRED) *****"
        + Style.RESET_ALL
    )


@pytest.fixture(scope="function")
def position_id_mat():
    logger.info(
        Fore.YELLOW
        + "***** TOIO MAT REQUIRED (POSITION ID MAT) *****"
        + Style.RESET_ALL
    )


@pytest.fixture(scope="function")
def standard_id_mat():
    logger.info(
        Fore.YELLOW
        + "***** TOIO MAT REQUIRED (STANDARD ID MAT) *****"
        + Style.RESET_ALL
    )


@pytest.fixture(scope="function")
def indicator():
    logger.info(Fore.YELLOW + "***** WATCH THE CUBE INDICATOR *****" + Style.RESET_ALL)
