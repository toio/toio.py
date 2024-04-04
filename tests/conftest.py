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


logger = getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
def wait():
    logger.info("PRE WAIT")
    time.sleep(2)


@pytest.fixture(scope="session", autouse=True)
def setup(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    capmanager.suspend_global_capture(in_=True)
    logger.info("***** GENERATE CONFIGURATION FILE: _cubes.py *****")
    logger.info("** This test requires a file '_cubes.py' that describes the cube to be used.")
    logger.info("** '_cube.py' is generated automatically.")
    logger.info("** To generate this, you turn on 2 cubes.")
    yn = input("Press Enter key when ready (If you don't need to generate, type 'skip' and Enter)")
    capmanager.resume_global_capture()
    if yn.lower() != "skip":
        logger.info("** GENERATE _cubes.py")
        os.system("python ./make_cube_list.py > _cubes.py")
        with open("_cubes.py", "r") as rf:
            logger.info(rf.read())
    else:
        logger.info("** SKIP")


@pytest.fixture(scope="function")
def confirm(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    yield  # At this point all the tests with this fixture are run

    capmanager.suspend_global_capture(in_=True)
    input("Press Enter key when ready")
    capmanager.resume_global_capture()


@pytest.fixture(scope="function")
def interactive(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    capmanager.suspend_global_capture(in_=True)
    logger.info("***** INTERACTIVE TEST (MANUAL CUBE OPERATION REQUIRED) *****")
    input("Press Enter key when ready")
    capmanager.resume_global_capture()


@pytest.fixture(scope="function")
def interactive_result(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    capmanager.suspend_global_capture(in_=True)
    logger.info("***** INTERACTIVE TEST (MANUAL CUBE OPERATION REQUIRED) *****")
    input("Press Enter key when ready")
    capmanager.resume_global_capture()

    yield  # At this point all the tests with this fixture are run

    capmanager.suspend_global_capture(in_=True)
    yn = input("\nIf this test fails, type 'N' and Enter. Otherwise, press Enter only")
    logger.info("%s", yn)
    capmanager.resume_global_capture()
    assert yn.lower() != "n"


@pytest.fixture(scope="function")
def position_id_mat(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    capmanager.suspend_global_capture(in_=True)
    logger.info("***** TOIO MAT REQUIRED (POSITION ID MAT) *****")
    input("Press Enter key when ready")
    capmanager.resume_global_capture()


@pytest.fixture(scope="function")
def standard_id_mat(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

    capmanager.suspend_global_capture(in_=True)
    logger.info("***** TOIO MAT REQUIRED (STANDARD ID MAT) *****")
    input("Press Enter key when ready")
    capmanager.resume_global_capture()


