# -*- coding: utf-8 -*-
# ************************************************************
#
#     install_to_pythonista3.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import io
import os
import shutil
import sys
import zipfile

import requests

from packaging.version import Version, parse

site_packages_dir = ""
DEVELOPMENT_MODE = False

if sys.platform != "ios":
    print("Platform '%s' is not supported" % sys.platform)
    if len(sys.argv) > 1 and sys.argv[1] == "--develop":
        print("development mode")
        DEVELOPMENT_MODE = True
        site_packages_dir = "./test_install/Documents/site-packages"
    else:
        exit(1)


def get_latest_toio_py(min="1.1.0a1", max="1.2.0"):
    min_ver = parse(min)
    max_ver = parse(max)
    latest = Version("0.0.0")
    found_specified_version = False
    # query = "https://pypi.org/pypi/toio-py/json"
    query = "https://test.pypi.org/pypi/toio-py/json"
    result = requests.get(query).json()
    # search latest version
    releases = result["releases"]
    for v in releases:
        ver = parse(v)
        if min_ver <= ver <= max_ver:
            found_specified_version = True
            if latest < ver:
                print("update latest:", v)
                latest = ver
    if not found_specified_version:
        print("toio.py package is not found")
        return None
    # get download url of latest version
    rel = result["releases"][str(latest)]
    for item in rel:
        fetch_url = False
        for key, value in item.items():
            if key == "filename" and "whl" in value:
                fetch_url = True
            if fetch_url and key == "url":
                return value

REQUIRED_WHLS = (
    "https://files.pythonhosted.org/packages/01/f3/936e209267d6ef7510322191003885de524fc48d1b43269810cd589ceaf5/typing_extensions-4.11.0-py3-none-any.whl",
    "https://files.pythonhosted.org/packages/08/4a/7b6ff6710ec58f6709000b1fbc27b763e3921a1e5f23032aebe2531366fa/bleak-0.21.1-py3-none-any.whl",
    get_latest_toio_py()
#    "https://toio.github.io/p3preview/assets/toio_py-1.1.0a2-py3-none-any.whl",
)

CLEANUP_TARGETS = (
    "typing_extensions",
    "bleak",
    "toio",
)

EXAMPLES = (
   "https://toio.github.io/internal-toio.py/angle_control.py",
   "https://toio.github.io/internal-toio.py/async_gather.py",
   "https://toio.github.io/internal-toio.py/async_gather_multi.py",
   "https://toio.github.io/internal-toio.py/async_task_group.py",
   "https://toio.github.io/internal-toio.py/basic_motor_control.py",
   "https://toio.github.io/internal-toio.py/concurrent_futures_simple.py",
   "https://toio.github.io/internal-toio.py/detect_mat.py",
   "https://toio.github.io/internal-toio.py/get_current_grid.py",
   "https://toio.github.io/internal-toio.py/get_information_1.py",
   "https://toio.github.io/internal-toio.py/get_information_2.py",
   "https://toio.github.io/internal-toio.py/get_standard_id.py",
   "https://toio.github.io/internal-toio.py/goto_a_gird.py",
   "https://toio.github.io/internal-toio.py/lamp.py",
   "https://toio.github.io/internal-toio.py/motor_control.py",
   "https://toio.github.io/internal-toio.py/move_to.py",
   "https://toio.github.io/internal-toio.py/multi_cubes_async_simple.py",
   "https://toio.github.io/internal-toio.py/multi_cubes_with_attribute.py",
   "https://toio.github.io/internal-toio.py/multi_cubes_with_named.py",
   "https://toio.github.io/internal-toio.py/read_position.py",
   "https://toio.github.io/internal-toio.py/scan_and_connect.py",
   "https://toio.github.io/internal-toio.py/sound.py",
   "https://toio.github.io/internal-toio.py/step.py",
   "https://toio.github.io/internal-toio.py/tutorial_pursuer.py",
)


if not DEVELOPMENT_MODE:
    for p in sys.path:
        if p.endswith("site-packages"):
            site_packages_dir = p
            break


assert site_packages_dir != ""
document_dir_index = site_packages_dir.split("/").index("Documents")
document_dir = "/".join(site_packages_dir.split("/")[: (document_dir_index + 1)])
example_dir = os.path.join(document_dir, "example_toio_py")
print("------------------------------------------------------------")
print("site package dir   : %s" % site_packages_dir)
print("document dir       : %s" % document_dir)
print("toio.py example dir: %s" % example_dir)
print("------------------------------------------------------------")
os.makedirs(site_packages_dir, exist_ok=True)
print("clean previous installation")
for filename in os.listdir(site_packages_dir):
    for cleanup in CLEANUP_TARGETS:
        if cleanup in filename:
            print("clean: %s" % filename)
            remove_target = os.path.normpath(os.path.join(site_packages_dir, filename))
            if os.path.isdir(remove_target):
                shutil.rmtree(remove_target)
            else:
                os.remove(remove_target)
print("------------------------------------------------------------")
print("install packages")
for whl in REQUIRED_WHLS:
    if whl is not None:
        print("install module: %s" % whl.split("/")[-1])
        zipfile.ZipFile(io.BytesIO(requests.get(whl).content)).extractall(site_packages_dir)
print("------------------------------------------------------------")
print("install examples")
if not os.path.isdir(example_dir):
    os.makedirs(example_dir, exist_ok=True)
    for example in EXAMPLES:
        filename = example.split("/")[-1]
        print("install toio.py example: %s" % filename)
        data = requests.get(example).content
        with open(os.path.join(example_dir, filename), "wb") as wfh:
            wfh.write(data)
else:
    print("SKIP: example files are already installed")
print("------------------------------------------------------------")
print("install completed")
print("")
print("restart Pythonista3")

if not DEVELOPMENT_MODE:
    import console

    console.alert("install completed", "Close Pythonista3, Please re-open", "OK", hide_cancel_button=True)
    exit()
