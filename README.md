# toio.py

[![PyPI](https://img.shields.io/pypi/v/toio-py?color=00aeca)](https://pypi.org/project/toio-py/)

This is a library for controlling [toio™Core Cube](https://toio.io/platform/cube/) from Python.

Based on [toio Core Cube Specifications](https://toio.github.io/toio-spec/en/) v2.3.0.

**（日本語版 README.md は[こちら](https://github.com/toio/toio.py/blob/main/README.ja.md)）**

## Features

- Uses [bleak](https://github.com/hbldh/bleak) for Bluetooth communication
- Supports Python 3.11 and later versions
- Multi-platform (Windows, Linux, macOS)
- No dedicated Bluetooth dongle required
- Asynchronous API (ToioCoreCube API) based on the toio Core Cube Specifications and synchronous API (SimpleCube API) for easy cube control
- Scanning function by specifying BLE addresses and cube-specific names
- API to control cube functions classified by characteristics (ToioCoreCube API)
- Ability to scan paired cubes (Windows only)

## System requirements

### Primaly tested environment

- Windows: Windows 10 (21H2)

### Secondary tested environment

- Linux: Ubuntu22.04
- macOS: macOS 12(Monterey)

## Setup and tutorial

See below for instructions on how to set up and run the tutorial.

- [Setup Guide (English)](https://github.com/toio/toio.py/blob/main/SETUP_GUIDE.en.md)
- [Setup Guide (Japanese)](https://github.com/toio/toio.py/blob/main/SETUP_GUIDE.ja.md)
- [Setup Guide (Chinese)](https://github.com/toio/toio.py/blob/main/SETUP_GUIDE.zh.md)

---

## SimpleCube API

See [SIMPLE_API.en.md](https://github.com/toio/toio.py/blob/main/SIMPLE_API.en.md) for information on the SimpleCube API for easily controlling toio Core Cubes.

- [SIMPLE_API.en.md (English)](https://github.com/toio/toio.py/blob/main/SIMPLE_API.en.md)
- [SIMPLE_API.ja.md (Japanese)](https://github.com/toio/toio.py/blob/main/SIMPLE_API.ja.md)

---

## API document

- [API Document](https://toio.github.io/toio.py/)

---

## Implementation overview

toio.py consists of two classes, Scanner and ToioCoreCube.

### Scanner

Class for scanning cubes via the BLE interface.

You can scan for cubes in the following ways:

- Scan for nearby cubes
- Scan for a specific cube by name (the last 3 characters of the toio Core Cube name)

The following is available only for Windows and Linux:

- Scan for a specific cube by BLE address

The following is available only for Windows:

- Scan for cubes registered (paired) with OS

### ToioCoreCube

Class for controlling the cube.

ToioCoreCube has subclasses corresponding to the characteristics described in [toio CoreCube Specifications](https://toio.github.io/toio-spec/). You access the various functions of the cube via these subclasses.

## Sample code

### Scan and connect

Use `BLEScanner.scan()`.

The argument is the number of cubes to find in the scan.

If the specified number of cubes are not found by the timeout (default value is 5 seconds), it returns a list of the number of cubes found at the time of the timeout.

The following sample scans and connects nearby cubes.

Disconnects 3 seconds after connecting.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan(num=1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Scan and connect (scan by cube name)

Use `BLEScanner.scan_with_id()`.

The argument is [set (set type)](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset), a 3-digit string at the end of the cube.
The argument is given as set even if only one unit is to be scanned.

If the specified number of cubes are not found by the timeout (default value is 5 seconds), it returns a list of cubes found at the time of the timeout.

```Python
    dev_list = await BLEScanner.scan_with_id(cube_id={"C7f"})
```

Scan and connect `toio Core Cube-C7f`.

Disconnects 3 seconds after connecting.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan_with_id(cube_id={"C7f"})
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Scan and connect (scan paired cubes: supported on Windows only)

Windows only, paired cubes can be scanned.

Use `BLEScanner.scan_registered_cubes()`.

The argument is the number of cubes to find in the scan.

If the specified number of cubes are not found by the timeout (default value is 5 seconds), it returns a list of the number of cubes found at the time of the timeout.

```Python
    dev_list = await BLEScanner.scan_registered_cubes()
```

Scan for paired cubes and connect them. (Pair the cube with Windows using "Add Bluetooth Device" before doing this.)

Disconnects 3 seconds after connecting.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan_registered_cubes(num=1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Get the cube location

Use the class `ToioCoreCube.api.id_information` to get the location information of the cube.
This class provides access to the [read sensor characteristic](https://toio.github.io/toio-spec/en/docs/ble_id).

The following code reads and displays the cube ID information 200 times.
It uses `read()` to read to the characteristic.

```Python
import asyncio

from toio import *

async def read_id():
    device_list = await BLEScanner.scan(1)
    assert len(device_list)
    cube = ToioCoreCube(device_list[0].interface)
    await cube.connect()
    for n in range(200):
        pos = await cube.api.id_information.read()
        print("%4d:%s" % (n, str(pos)))
    await cube.disconnect()

if __name__ == "__main__":
    asyncio.run(read_id())
```

### Get the cube location (using notification)

You can receive notifications from the cube by registering a notification handler with `register_notification_handler()`.
Notifications are per each characteristic. A notification handler registered with `ToioCoreCube.api.id_information.register_notification_handler()` receives
receive only notifications from the read sensor.

The following code reads the ID by notification.

After 10 seconds, the handler is unregistered and disconnected.

```Python
import asyncio

from toio import *

# Notification handler
def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))


async def read_id():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    # add notification handler
    await cube.api.id_information.register_notification_handler(notification_handler)
    await asyncio.sleep(10)

    # remove notification handler
    await cube.api.id_information.unregister_notification_handler(
        notification_handler
    )
    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(read_id())
```

The complete code that keeps displaying ID information until Ctlr-C is pressed is [examples/read_position.py](https://github.com/toio/toio.py/blob/main/examples/read_position.py).

### Motor control

The `ToioCoreCube.api.motor` class is used to control the motor.
This class provides access to the [motor's characteristic](https://toio.github.io/toio-spec/en/docs/ble_motor).

The following code uses `motor_control()` to rotate the cube in place for 2 seconds.

```Python
import asyncio

from toio import *

async def motor_1():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    # go
    await cube.api.motor.motor_control(10, -10)
    await asyncio.sleep(2)
    # stop
    await cube.api.motor.motor_control(0, 0)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(motor_1())
```

### Motor control (move to specified position)

Use `motor.motor_control_target()` to move the cube to a specified position on the mat.

```Python
import asyncio

from toio import *

# Notification handler
def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))

async def motor_2():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    await cube.api.motor.register_notification_handler(notification_handler)
    await cube.api.motor.motor_control_target(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(
            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration),
        target=TargetPosition(
            cube_location=CubeLocation(point=Point(x=200, y=200), angle=0),
            rotation_option=RotationOption.AbsoluteOptimal,
        ),
    )

    await asyncio.sleep(4)
    await cube.disconnect()

if __name__ == "__main__":
    asyncio.run(motor_2())
```

### Motor control (move to multiple specified positions)

Use `motor.motor_control_multiple_targets()` to move the cube to a specified position on multiple mats.

```Python
import asyncio

from toio import *

async def motor_3():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    targets = [
        TargetPosition(
            cube_location=CubeLocation(point=Point(x=250, y=250), angle=0), rotation_option=RotationOption.AbsoluteOptimal
        ),
        TargetPosition(
            cube_location=CubeLocation(point=Point(x=120, y=170), angle=0), rotation_option=RotationOption.AbsoluteOptimal
        ),
    ]
    await cube.api.motor.motor_control_multiple_targets(
        timeout=5,
        movement_type=MovementType.Linear,
        speed=Speed(
            max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration),
        mode=WriteMode.Overwrite,
        target_list=targets,
    )

    await asyncio.sleep(5)
    await cube.disconnect()

if __name__ == "__main__":
    asyncio.run(motor_3())
```
