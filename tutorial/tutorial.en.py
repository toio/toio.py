# %% [markdown]
# # toio.py Tutorial (for v1.1)
#
# In this tutorial, we will create a program using toio.py.
# The program works by placing one cube on the mat and the other cube comes up to the placed cube.
#
# This tutorial uses two cubes and a developer's mat.
#

# This tutorial uses Visual Studio Code's
# [Code Cell feature](https://code.visualstudio.com/docs/python/jupyter-support-py#_jupyter-code-cells)
# to show how it works in practice.
#
# This tutorial is intended for people with a basic knowledge of Python.
# There is no explanation of Python syntax or basic usage.
#


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
!pip install typing-extensions
!pip install bleak
!pip install toio-py --upgrade
!pip install ipykernel


# %% [markdown]
# ## Check the environment
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
if sys.version_info.major == 3 and 8 <= sys.version_info.minor <= 12:

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


# --------------------------------------------------------------------------------
# %% [markdown]
# # Scan, Connection and Disconnection
#
# ## ToioCoreCube.scan()
# ## ToioCoreCube.connect()
# ## ToioCoreCube.disconnect()
#
# Usage Example and Description
# ```Python
#    await cube.scan()
#    await cube.connect()
#    await cube.disconnect()
# ```
#
# Create an instance of ToioCoreCube to scan, connect, and disconnect.
# Call `scan()` and `connect()` to actually connect to the cube and allow it to communicate.
#
# To disconnect, call `disconnect()`.
#
# `scan()`, `connect()` and `disconnect()` are asynchronous functions, so use `await` to wait for them to complete.
#
# The following code connects to the cube and disconnects after 1 second.

import asyncio

from toio.cube import ToioCoreCube

try:
    cube = ToioCoreCube()
    await cube.scan()
    await cube.connect()
    print("Connected")
    await asyncio.sleep(1)
    await cube.disconnect()
    print("Disconnected")
except:
    print("No cubes found")

# --------------------------------------------------------------------------------
# %% [markdown]
# # Scan, Connection and Disconnection with context manager
#
# ## ToioCoreCube()
#
# Usage Example and Description
# ```Python
#    async with ToioCoreCube()
# ```
#
# Since ToioCoreCube class is a context manager, you can easily scan, connect, and
# disconnect cubes by using `async with`.
#
# The following code connects to the cube and disconnects after 1 second.

import asyncio

from toio.cube import ToioCoreCube

async with ToioCoreCube() as cube:
    print("Connected")
    await asyncio.sleep(1)
print("Disconnected")


# --------------------------------------------------------------------------------
# %% [markdown]
# # Scan, Connection and Disconnection multiple cubes
#
# ## MultipleToioCoreCubes()
#
# Usage Example and Description
# ```Python
#    async with MultipleToioCoreCubes()
# ```
#
# MultipleToioCoreCubes class can be used to scan, connect, and disconnect multiple cubes.
# MultipleToioCoreCubes class is a context manager like ToioCoreCube class, so you can easily
# scan, connect, and disconnect cubes by using `async with`.
#
# The following code connects to two cubes and disconnects after 1 second.

import asyncio

from toio.cube.multi_cubes import MultipleToioCoreCubes

async with MultipleToioCoreCubes(cubes=2) as cubes:
    print("Connected to %s" % cubes[0].name)
    print("Connected to %s" % cubes[1].name)
    await asyncio.sleep(1)
print("Disconnected")


# --------------------------------------------------------------------------------
# %% [markdown]
# # Access to each Cube feature
#
# You can now scan, connect, and disconnect cubes.
# Next, we will control various functions of the cube.
#
# Before actually controlling functionality, give an overview of how functionality is accessed with toio.py.
#
# The `ToioCoreCube` class has a`api` subclass.
# All the classes and functions needed to control the functionality of the cubes are under this `api` subclass.
#
# ## ToioCoreCube.api
#
# The `ToioCoreCube.api` class is a collection of interface classes for accessing various functions of the cube.
#
# ### ToioCoreCube.api.( interface class name)
#
# Interface classes for accessing various features.
#
# Interface classes are created per [Technical Specification Characteristic] (https://toio.github.io/toio-spec/en/docs/ble_communication_overview#using-the-cubes-functions).
# For the functionality of each interface class, please refer to the DocString for each class.
#
# Interface Class Examples
#
# - id_information: Class that handles ID reading function
# - indicator: Classes that control the ramp of a cube
# - motor: Class that controls the motor on the cube
#

from toio.cube import ToioCoreCube
from toio.cube.api.base_class import CubeCharacteristic

async with ToioCoreCube() as cube:
    for key, value in vars(cube.api).items():
        if isinstance(value, CubeCharacteristic):
            print(f"{key:20s}: <interface class>")
        elif not key.startswith("_"):
            print(f"{key:20s}: {value}")


# --------------------------------------------------------------------------------
# %% [markdown]
# ## Interface Classes
#
# Interface classes for accessing various features have some common methods.
#
# ### Common static method
#
# #### `is_my_data(data:bytearray)`
#
# Each interface class has a `is_my_data(data:bytearray)` static method.
#`is_my_data()` returns the object corresponding to its argument if it is own characteristic read or notification data, otherwise it returns `None`.
#
# ### Common methods
#
# #### `register_notification_handler(handler: CubeNotificationHandler)`
#
# Register the notification handler function (see below).
#
# #### `unregister_notification_handler(handler: CubeNotificationHandler)`
#
# Unregister the Notification Handler function (see below).
#

# --------------------------------------------------------------------------------
# %% [markdown]
# # Reading ID
#
# ## ToioCoreCube.api.id_information.read()
#
# Usage Example and Description
# ```Python
#    read_data = await cube.api.id_information.read()
# ```
#
# Read from the [ID Information characteristic](https://toio.github.io/toio-spec/en/docs/ble_id).
#
# 'read_data' can be one of the following objects or a `None`:
# If 'read_data' does not match the format of the objects listed below, the return value of `read()` will be`None`.
#
# (`id_information.read()` internally calls the characteristic static method`IdInformation.is_my_data()`)
#
# - PositionId
# - StandardId
# - PositionIdMissed
# - StandardIdMissed
#
# ### Objects returned by `id_information.read()`
#
# #### PositionId
#
# This object indicates that the cube has detected a Position ID.
#
# Attributes of PositionId
#
# | Attribute        | Type         |                                  |
# | ---------------- | ------------ | -------------------------------- |
# | center           | CubeLocation | Center position of the cube      |
# | sensor           | CubeLocation | ID Sensor position of the cube   |
#
# #### StandardId
#
# This object indicate that the cube has detected a Standard ID.
#
# Attributes of StandardId
#
# | Attribute        | Type         |                                  |
# | ---------------- | ------------ | -------------------------------- |
# | value            | int          | Standard ID type                 |
# | angle            | int          | Angle of the cube                |
#
# #### PositionIdMissed
#
# This object indicates that the Cube has been removed from above the Position ID.
#
# #### StandardIdMissed
#
# This object indicates that the Cube has been removed from above the Standard ID.
#
# The code below performs `id_information.read()` 200 times and displays the content read.

from toio.cube import ToioCoreCube

async with ToioCoreCube() as cube:
    print("start")
    for n in range(200):
        read_data = await cube.api.id_information.read()
        if read_data is not None:
            print(n, type(read_data), read_data)
    print("end")


# --------------------------------------------------------------------------------
# %% [markdown]
# # Reading ID by notification handler
#
# ## ToioCoreCube.api.id_information.register_notification_handler()
# ## ToioCoreCube.api.id_information.unregister_notification_handler()
#
# Usage Example and Description
# ```Python
#    await cube.api.id_information.register_notification_handler(handler)
#    await cube.api.id_information.unregister_notification_handler(handler)
# ```
#
# The information that can be obtained with `read()` is the information that the cube has at the time of performing` read()`.
# `read()` only gives the most recent information, so multiple attempts of` read()` do not get the information that changed between each call.
#
# The cube has a notification function that voluntarily sends detection ID information.
# By setting a notification handler function, the information detected by the cube can be received on the Python side without omission.
#
# `register_notification_handler()` registers the notification handler function.
# `unregister_notification_handler()` unregisters the notification handler function.
#
# ## Notification handler function
#
# The notification handler function has a single `bytearray` argument and returns nothing.
#
# The notification handler function can be synchronous or asynchronous.
# If the notification handler function is an asynchronous function, the notification handler function can
# execute processing that uses `await` internally.
#
# The argument of the notification handler function is the data in bytes notified from the cube.
#
# The following code registers a handler function in id_information and receives notification from the
# cube for 10 seconds and displays it.

import asyncio

from toio.cube import ToioCoreCube, IdInformation

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))

async with ToioCoreCube() as cube:
    print("start")
    await cube.api.id_information.register_notification_handler(notification_handler)
    await asyncio.sleep(10)
    await cube.api.id_information.unregister_notification_handler(
        notification_handler
    )
    print("end")

# --------------------------------------------------------------------------------
# %% [markdown]
# # Motor control
#
# ## ToioCoreCube.api.motor.motor_control()
#
# Usage Example and Description
# ```Python
#    await cube.api.motor.motor_control(10, 10)
#    await cube.api.motor.motor_control(0, 0)
#    await cube.api.motor.motor_control(50, -50, 1000)
# ```
#
# Move the cube by specifying left and right motor speeds.
#
# The third argument is optional and specifies the motor drive time. It is in milliseconds [ms].
#  (Specify 1000 if you want to run for 1 second)
#
# The code below moves the cube forward for 2 seconds at speed 10, then rotates it for 1 second at speed 50.

import asyncio

from toio.cube import ToioCoreCube

async with ToioCoreCube() as cube:
    print("go forward")
    await cube.api.motor.motor_control(10, 10)
    await asyncio.sleep(2)
    print("stop")
    await cube.api.motor.motor_control(0, 0)
    print("spin turn (1000[ms])")
    await cube.api.motor.motor_control(50, -50, 1000)
    await asyncio.sleep(2)
    print("end")


# --------------------------------------------------------------------------------
# %% [markdown]
# # Motor control (move to specified position)
#
# ## ToioCoreCube.api.motor.motor_control_target()
#
# Usage Example and Description
# ```Python
#    await cube.api.motor.motor_control_target(
#        timeout=5,
#        movement_type=MovementType.Linear,
#        speed=Speed(
#            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
#        ),
#        target=TargetPosition(
#            cube_location=CubeLocation(point=Point(x=200, y=200), angle=0),
#            rotation_option=RotationOption.AbsoluteOptimal,
#        ),
#    )
# ```
#
# Moves the cube to the specified coordinates on the mat.
#
# ## Arguments
#
# ### timeout
#
# Specifies the timeout period. The unit is seconds [s].
# If 0 is specified, the timeout time is 10 seconds.
# A timeout period of 0 seconds cannot be specified.
#
# ### movement_type
#
# Specifies the movement type.
#
# | Value                             | Description                                    |
# | --------------------------------- | ---------------------------------------------- |
# | MovementType.Curve                | Move while rotating                            |
# | MovementType.CurveWithoutReverse  | Move while rotating (without moving backwards) |
# | MovementType.Linear               | Rotate after moving                            |
#
# ### speed
#
# Specifies the speed parameter.
#
# The speed parameter consists of `max` and`speed_change_type`.
#
# #### max
#
# Specifies the maximum speed. The speed can be specified in the range 0 to 255.
#
# #### speed_change_type
#
# Specifies the speed change type.
#
# | Value                                       | Description                                                                                           |
# | ------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
# | SpeedChangeType.Constant                    | Speed constant                                                                                        |
# | SpeedChangeType.Acceleration                | Gradual acceleration towards the target point                                                         |
# | SpeedChangeType.Deceleration                | Gradual deceleration towards the target point                                                         |
# | SpeedChangeType.AccelerationAndDeceleration | Gradual acceleration halfway until the target point, then deceleration from there to the target point |
#
# ### target
#
# Specifies the target location parameter.
#
# Target location parameter consists of `cube_location` and` rotation_option`
#
# #### cube_location
#
# Specifies the cube location information.
#
# Cube location information consists of `Point` and` angle`
#
# ##### Point
#
# Specifies the coordinates of the cube in `x``y`.
#
# ##### angle
#
# Specifies the cube angle. Specify between 0 and 360.
#
# #### rotation_option
#
# Specifies additional information about the angle of the cube at the target location.
#
# | Value                           | Angle                           | Direction of rotation                   |
# | --------------------------------| ------------------------------- | --------------------------------------- |
# | RotationOption.AbsoluteOptimal  | Absolute                        | Direction with small amount of rotation |
# | RotationOption.AbsolutePositive | Absolute                        | Forward direction                       |
# | RotationOption.AbsoluteNegative | Absolute                        | Negative direction                      |
# | RotationOption.RelativePositive | Relative                        | Forward direction                       |
# | RotationOption.RelativeNegative | Relative                        | Negative direction                      |
# | RotationOption.WithoutRotation  | (No angle specified)            | No rotation                             |
# | RotationOption.SameAsWriting    | (Same as with write operation)  | Direction with small amount of rotation |
#
# The code below will move the cube to coordinates (200, 200) on the Developer Mat.
#
# The result of the move is obtained with the notification handler function.
#
# Please run it after placing the cube on the developer mat.

import asyncio
from toio import *

def notification_handler(payload: bytearray):
    motor_info = Motor.is_my_data(payload)
    print(type(motor_info), str(motor_info))

async with ToioCoreCube() as cube:
    await cube.api.motor.register_notification_handler(notification_handler)
    await cube.api.motor.motor_control_target(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(
            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
        ),
        target=TargetPosition(
            cube_location=CubeLocation(point=Point(x=200, y=200), angle=0),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
    )

    await asyncio.sleep(5)
    await cube.api.motor.unregister_notification_handler(notification_handler)


# --------------------------------------------------------------------------------
# %% [markdown]
# # Control of two cubes
#
# We are aiming to complete this by combining the existing features.
#
# Scan the two cubes and connect them.
#
# Turn on the lamp of the first cube green and
# register a notification handler function to read the coordinate information.
# If the notification from the cube is a Position ID, store the coordinates of
# the center of the cube in the global variable `green_cube_location`.
#
# The light on the second cube should turn red and rotate for 1 second.
#
# 10 seconds after the second cube connects, disconnects from all cubes and exits.

import asyncio
from toio import *


green_cube_location = None

def id_notification_handler(payload: bytearray):
    global green_cube_location
    id_info = IdInformation.is_my_data(payload)
    if isinstance(id_info, PositionId):
        green_cube_location = id_info.center
        print(str(green_cube_location))

async with MultipleToioCoreCubes(cubes=2) as cubes:
    cube_green = cubes[0]
    cube_red = cubes[1]

    red = IndicatorParam(
        duration_ms = 0,
        color = Color(r = 255, g = 0, b = 0)
    )

    green = IndicatorParam(
        duration_ms = 0,
        color = Color(r = 0, g = 255, b = 0)
    )
    await cube_green.api.indicator.turn_on(green)
    await cube_red.api.indicator.turn_on(red)

    print("start")
    await cube_green.api.id_information.register_notification_handler(id_notification_handler)
    await cube_red.api.motor.motor_control(30, -30, 1000)

    await asyncio.sleep(10)

    await cube_green.api.id_information.unregister_notification_handler(
        id_notification_handler
    )
    print("end")


# --------------------------------------------------------------------------------
# %% [markdown]
# # Completion of tutorial program
#
# Change the second cube's movement method from simple motor control to moving to specified coordinates.
#
# The target location of the second cube is the coordinate obtained in the notification handler of the first cube.
# The coordinates are shared via the global variable `green_cube_location`.
#

import asyncio
from toio import *


green_cube_location = None
red_cube_arrived = True

def id_notification_handler(payload: bytearray):
    global green_cube_location
    id_info = IdInformation.is_my_data(payload)
    if isinstance(id_info, PositionId):
        green_cube_location = id_info.center

def motor_notification_handler(payload: bytearray):
    global red_cube_arrived
    motor_response = Motor.is_my_data(payload)
    if isinstance(motor_response, ResponseMotorControlTarget):
        print(motor_response)
        red_cube_arrived = True

async with MultipleToioCoreCubes(cubes=2) as cubes:
    cube_green = cubes[0]
    cube_red = cubes[1]

    red = IndicatorParam(
        duration_ms = 0,
        color = Color(r = 255, g = 0, b = 0)
    )

    green = IndicatorParam(
        duration_ms = 0,
        color = Color(r = 0, g = 255, b = 0)
    )
    await cube_green.api.indicator.turn_on(green)
    await cube_red.api.indicator.turn_on(red)

    print("start")
    await cube_green.api.id_information.register_notification_handler(id_notification_handler)
    await cube_red.api.motor.register_notification_handler(motor_notification_handler)

    for _ in range(30):
        if green_cube_location is not None and red_cube_arrived:
            red_cube_arrived = False
            print("cube_red: move to", str(green_cube_location))
            await cube_red.api.motor.motor_control_target(
                timeout=5,
                movement_type=MovementType.Linear,
                speed=Speed(
                    max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
                ),
                target=TargetPosition(
                    cube_location=green_cube_location,
                    rotation_option=RotationOption.AbsoluteOptimal,
                ),
            )

        await asyncio.sleep(1)

    await cube_red.api.motor.unregister_notification_handler(
        motor_notification_handler
    )
    await cube_green.api.id_information.unregister_notification_handler(
        id_notification_handler
    )
    print("end")



# --------------------------------------------------------------------------------
# %% [markdown]
# # Tutorial finished
#
# Thank you for your support. The tutorial is now complete.
#
# The final code for this tutorial is the `tutorial_pursuer.py` in the example directory,
# which enables execution of the code as a single program rather than as a code-cell function.
#
# There are several additional example programs in the example directory.
# As a next step, you may want to try modifying the example program yourself.
#
# ## List of example programs
#
# | Example                      | Description                             |
# | ---------------------------- | --------------------------------------- |
# | examples/detect_mat.py       | Reads coordinates and displays mat type |
# | examples/motor_control.py    | Motor control                           |
# | examples/multi.py            | Scanning and connecting multiple cubes  |
# | examples/read_position.py    | Reading ID information                  |
# | examples/scan_and_connect.py | Scanning and connecting                 |
# | examples/tutorial_pursuer.py | Final code for this tutorial            |

# --------------------------------------------------------------------------------
# %% [markdown]
# # Supplementary information: How to execute asynchronous processing without using a code cell
#
# There are a few things to keep in mind when writing programs that handle
# asynchronous processing, such as toio.py, without using the code-cell feature.
#
#
# `await` can only be used inside asynchronous functions.
# (This can be called directly with the code cell function)
#
# When using asynchronous processing like toio.py, first create an asynchronous function, and then
# execute that asynchronous function with `asyncio.run()`
#
# **Example: A simple Python program that performs asynchronous processing**
#
# ```Python
# #!/usr/bin/env python
#
# import asyncio
# from toio import *
#
# async def cube_functions():
#     dev_list = await BLEScanner.scan(1)
#     assert len(dev_list)
#     cube = ToioCoreCube(dev_list[0].interface)
#     await cube.connect()
#     await cube.disconnect()
#
# asyncio.run(cube_functions())
# ```


# %%
