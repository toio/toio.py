# %% [markdown]
# # Quickstart toio.py
#
# This example uses a cube and a developer's mat.
#

# This example uses Visual Studio Code's
# [Code Cell feature](https://code.visualstudio.com/docs/python/jupyter-support-py#_jupyter-code-cells)
# to show how it works in practice.
#
# This example is intended for people with a basic knowledge of Python.
# There is no explanation of Python syntax or basic usage.
#
# This example is run on Python **3.11** only.
# Other version is not supported.
#
# Check Python version...

import sys

print(
    "Python version (%d.%d) : " % (sys.version_info.major, sys.version_info.minor),
    end="",
)
if sys.version_info.major == 3 and sys.version_info.minor == 11:
    print("OK")
else:
    print("NG")
    print("python %d.%d is not supported (use python 3.11)" % (
          sys.version_info.major, sys.version_info.minor))

# --------------------------------------------------------------------------------
# %% [markdown]
## Install required packages
#
# Execute the following script in the Visual Studio Code code cell.
#
# To run the cell code, click on the area labeled `Run Cell` in Visual Studio Code.
# This tutorial uses cells to test functionality.
# Make sure you have mastered how to execute the cell code at this point.
#

!pip install setuptools --upgrade
!pip install toio-py --upgrade
!pip install bleak
!pip install ipykernel


# %% [markdown]
# ## Confirm your environment
#
# Execute the following script in the VS Code code cell.
#
# If all displays `OK`, then the required software has been installed correctly.
#

import sys

print(
    "Python version (%d.%d) : " % (sys.version_info.major, sys.version_info.minor),
    end="",
)
if sys.version_info.major == 3 and sys.version_info.minor == 11:
    print("OK")
    print("%-22s: " % "bleak", end="")
    try:
        import bleak
    except ImportError:
        print("NG (not installed)")
        sys.exit(1)
    print("OK")

    print("%-22s: " % "toio", end="")
    try:
        import toio
    except ImportError:
        print("NG (not installed)")
        sys.exit(1)
    print("OK")
else:
    print("NG")
    print("python %d.%d is not supported (use python 3.11)" % (
          sys.version_info.major, sys.version_info.minor))


# --------------------------------------------------------------------------------
# %% [markdown]
# # Example 1: Illuminate the indicator light
#
# Illuminate the indicator light with pink color
# at the bottom of Cube on connection.
#
# If you want to stop, click on 'Interrupt'
# in the upper left corner of the Juypter interactive tab.

import asyncio

from toio.cube import Color, IndicatorParam, ToioCoreCube
from toio.device_interface import CubeInfo
from toio.scanner import BLEScanner

async def example1():
    print("search cubes")
    found_cubes: list[CubeInfo] = await BLEScanner.scan(num=1)
    if len(found_cubes) == 0:
        print("no cubes are found!")
    else:
        print("connect to the cube")
        async with ToioCoreCube(found_cubes[0].interface) as cube:
            print("turn on the cube lamp")
            await cube.api.indicator.turn_on(
                IndicatorParam(color=Color(r=255, g=105, b=180), duration_ms=0)
            )
            print("click 'interrupt' to stop")
            try:
                while True:
                    await asyncio.sleep(0)
            except:
                pass
            print("disconnecting with the cube")
        print("disconnected")
    print("end")

await example1()

# --------------------------------------------------------------------------------
# %% [markdown]
# # Example 2: Move
#
# Cube moves forward with a certain speed and duration on connection.
#
# If you want to stop, click on 'Interrupt'
# in the upper left corner of the Juypter interactive tab.

import asyncio

from toio.cube import ToioCoreCube
from toio.device_interface import CubeInfo
from toio.scanner import BLEScanner

async def example2():
    print("search cubes")
    found_cubes: list[CubeInfo] = await BLEScanner.scan(num=1)
    if len(found_cubes) == 0:
        print("no cubes are found!")
    else:
        print("connect to the cube")
        async with ToioCoreCube(found_cubes[0].interface) as cube:
            print("run the cube")
            await cube.api.motor.motor_control(left=50, right=50, duration_ms=1000)
            print("click 'interrupt' to stop")
            try:
                while True:
                    await asyncio.sleep(0)
            except:
                pass
            print("disconnecting with the cube")
        print("disconnected")
    print("end")

await example2()

# --------------------------------------------------------------------------------
# %% [markdown]
# # Example 2: Move (works with the developers mat)
#
# If you have Developer Mat, by this code,
# Cube always move to center of the map wherever Cube is placed. 
#
# If you want to stop, click on 'Interrupt'
# in the upper left corner of the Juypter interactive tab.

import asyncio

from toio.cube import (
    MovementType,
    RotationOption,
    Speed,
    SpeedChangeType,
    TargetPosition,
    ToioCoreCube,
)
from toio.position import CubeLocation, ToioMat
from toio.scanner import BLEScanner

async def example2_2():
    cube_speed = Speed(max=100, speed_change_type=SpeedChangeType.Constant)
    target_center_of_mat = TargetPosition(
        cube_location=CubeLocation(
            point=ToioMat.SimpleMat.center(), angle=0
        ),
        rotation_option=RotationOption.WithoutRotation,
    )

    print("search cubes")
    found_cubes: list[CubeInfo] = await BLEScanner.scan(num=1)
    if len(found_cubes) == 0:
        print("no cubes are found!")
    else:
        print("connect to the cube")
        async with ToioCoreCube(found_cubes[0].interface) as cube:
            print("move to center")
            print("loop until interrupted")
            try:
                while True:
                    await cube.api.motor.motor_control_target(
                        timeout=10,  # timeout 5[s]:
                        movement_type=MovementType.Curve,
                        speed=cube_speed,
                        target=target_center_of_mat,
                    )
                    await asyncio.sleep(0.1)
            except:
                pass
            print("disconnecting with the cube")
        print("disconnected")
    print("end")

await example2_2()

# --------------------------------------------------------------------------------
# %% [markdown]
# # Example 3: Play sound by touching Developer Mat
#
# By using this code, a sound plays when Cube touches “7” card
# on the Developer Mat.
#
# In this sample, the sound comes from a cube.
# If you want to play the sound in a different way,
# replace the following with the appropriate API: 
#
# * Play sound
# ```
# await cube.api.sound.play_midi(
#     repeat=0,#
#     midi_notes=(
#         MidiNote(duration_ms=1000, note=Note.C6, volume=255),
#     ),
# )
# ```
#
# * Stop sound
# ```
# await cube.api.sound.play_midi(
#     repeat=1,
#     midi_notes=(
#         MidiNote(duration_ms=10, note=Note.NO_SOUND, volume=0),
#     ),
# )
# ```
#
# If you want to stop, click on 'Interrupt'
# in the upper left corner of the Juypter interactive tab.

import asyncio

from toio.cube import (
    IdInformation,
    IdInformationResponseType,
    MidiNote,
    Note,
    StandardId,
    ToioCoreCube,
)
from toio.device_interface import CubeInfo
from toio.scanner import BLEScanner
from toio.standard_id import StandardIdCard

# Use semaphores for exclusive control between event handlers and main loop
SEM: asyncio.Semaphore = asyncio.Semaphore(1)
ON_NUMBER_7: bool = False

# toio ID Notification from a cube
#
# Whether the cube is touching the mat is detected by the 
# notification handler.
# 
async def id_notification_handler(payload: bytearray):
    id_info: IdInformationResponseType | None = IdInformation.is_my_data(payload)
    # get the semaphore and then update the value 
    async with SEM:
        global ON_NUMBER_7
        if isinstance(id_info, StandardId) and id_info.value == StandardIdCard.NUMBER_7:
            ON_NUMBER_7 = True
        else:
            ON_NUMBER_7 = False

# main loop
async def example3():
    print("search cubes")
    found_cubes: list[CubeInfo] = await BLEScanner.scan(num=1)
    if len(found_cubes) == 0:
        print("no cubes are found!")
    else:
        print("connect to the cube")
        async with ToioCoreCube(found_cubes[0].interface) as cube:
            print("connected")
            await cube.api.id_information.register_notification_handler(
                id_notification_handler
            )
            sound_state: str = "off"
            print("loop until interrupted")
            try:
                while True:
                    await asyncio.sleep(0)
                    async with SEM:
                        request_sound_on = ON_NUMBER_7
                    if request_sound_on:
                        if sound_state == "off":
                            print("play sound")
                            await cube.api.sound.play_midi(
                                repeat=0,
                                midi_notes=(
                                    MidiNote(duration_ms=1000, note=Note.C6, volume=255),
                                ),
                            )
                            sound_state = "on"
                    else:
                        if sound_state == "on":
                            print("stop sound")
                            await cube.api.sound.play_midi(
                                repeat=1,
                                midi_notes=(
                                    MidiNote(duration_ms=10, note=Note.NO_SOUND, volume=0),
                                ),
                            )
                            sound_state = "off"
            except:
                pass
            print("disconnecting with the cube")
        print("disconnected")
    print("end")

await example3()

# %%
