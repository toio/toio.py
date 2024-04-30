# toio.py

[![PyPI](https://img.shields.io/pypi/v/toio-py?color=00aeca)](https://pypi.org/project/toio-py/)

This is a library for controlling [toio™Core Cube](https://toio.io/platform/cube/) from Python.

Based on [toio Core Cube Specifications](https://toio.github.io/toio-spec/en/) v2.4.0.

**（日本語版 README.md は[こちら](./blob/main/README.ja.md)）**

## Features

- Uses [bleak](https://github.com/hbldh/bleak) for Bluetooth communication
- Supports Python 3.8 and later versions (Python 3.12 is recommended)
- Multi-platform (Windows, Linux, macOS, iOS, iPadOS)
- No dedicated Bluetooth dongle required
- Asynchronous API (ToioCoreCube API) based on the toio Core Cube Specifications and synchronous API (SimpleCube API) for easy cube control
- Scanning function by specifying BLE addresses and cube-specific names
- API to control cube functions classified by characteristics (ToioCoreCube API)
- Ability to scan paired cubes (Windows only)

## System requirements

### Primary tested environment

- Windows: Windows 10 (21H2)

### Secondary tested environment

- Linux: Ubuntu22.04
- macOS: macOS 13(Ventura)

### Experimental implementation

- iOS, iPadOS: 17

toio.py works on Pythonista3.  
[How to install: INSTALL_TO_PYTHONISTA3.en.md](https://toio.github.io/toio.py/INSTALL_TO_PYTHONISTA3.en.html)


## Setup and tutorial

See below for instructions on how to set up and run the tutorial.

- [Setup Guide (English)](./blob/main/SETUP_GUIDE.en.md)
- [Setup Guide (Japanese)](./blob/main/SETUP_GUIDE.ja.md)
- [Setup Guide (Chinese)](./blob/main/SETUP_GUIDE.zh.md)

---

## SimpleCube API

See [SIMPLE_API.en.md](./blob/main/SIMPLE_API.en.md) for information on the SimpleCube API for easily controlling toio Core Cubes.

- [SIMPLE_API.en.md (English)](./blob/main/SIMPLE_API.en.md)
- [SIMPLE_API.ja.md (Japanese)](./blob/main/SIMPLE_API.ja.md)

---

## API document

- [API Document](https://toio.github.io/toio.py/)

---

## Implementation overview

toio.py consists of following classes:

### ToioCoreCube

Class for controlling the cube.

ToioCoreCube has subclasses corresponding to the characteristics described in [toio CoreCube Specifications](https://toio.github.io/toio-spec/). You access the various functions of the cube via these subclasses.

#### Features added since v1.1:

ToioCoreCube class includes basic scanner function.
ToioCoreCube class can scan a toio Core Cube without the help of the Scanner class.
For scanning in special settings. use the Scanner class.

### Scanner

Class for scanning cubes via the BLE interface.

You can scan for cubes in the following ways:

- Scan for nearby cubes
- Scan for a specific cube by name (the last 3 characters of the toio Core Cube name)

The following is available only for Windows and Linux:

- Scan for a specific cube by BLE address

The following is available only for Windows:

- Scan for cubes registered (paired) with OS

### MultipleToioCoreCubes

MultipleToioCoreCubes class is added since v1.1.

MultipleToioCoreCubes is supplementary helper class to control multiple toio Core Cubes.

This class provides several functions for multiple toio Core Cubes such as connect, disconnect, etc.

## Examples

### Scan and connect

Create a ToioCoreCube instance with `ToioCoreCube()` without parameters and call `scan()` and `connect()`.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    cube = ToioCoreCube()
    await cube.scan()
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

Since `ToioCoreCube()` is an asynchronous context manager, you can use `async with` to implicitly scan, connect, and disconnect.  
The preceding code can be written as follows using `async with`:

```Python
import asyncio

from toio import *

async def scan_and_connect():
    async with ToioCoreCube() as cube:

        await asyncio.sleep(3)

    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Scan and connect using Scanner class

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

### Scan and connect using Scanner class (scan by cube name)

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

### Scan and connect using Scanner class (scan paired cubes: supported on Windows only)

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
    async with ToioCoreCube() as cube:
        for n in range(200):
            pos = await cube.api.id_information.read()
            print("%4d:%s" % (n, str(pos)))

if __name__ == "__main__":
    asyncio.run(read_id())
```

### Get the cube location (using notification)

You can receive notifications from the cube by registering a notification handler with `register_notification_handler()`.
Notifications are per each characteristic. A notification handler that registered with `ToioCoreCube.api.id_information.register_notification_handler()` receives
only notifications from the read sensor.

The following code reads the ID by notification.

After 10 seconds, the handler is unregistered and disconnected.

```Python
import asyncio

from toio import *

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))


async def read_id():
    async with ToioCoreCube() as cube:
        # add notification handler
        await cube.api.id_information.register_notification_handler(notification_handler)

        await asyncio.sleep(10)

        # remove notification handler
        await cube.api.id_information.unregister_notification_handler(
            notification_handler
        )
    return 0

if __name__ == "__main__":
    asyncio.run(read_id())
```

The complete code that keeps displaying ID information until Ctrl-C is pressed is [examples/read_position.py](https://github.com/toio/toio.py/blob/main/examples/read_position.py).

### Motor control

The `ToioCoreCube.api.motor` class is used to control the motor.
This class provides access to the [motor's characteristic](https://toio.github.io/toio-spec/en/docs/ble_motor).

The following code uses `motor_control()` to rotate the cube in place for 2 seconds.

```Python
import asyncio

from toio import *

async def motor_1():
    async with ToioCoreCube() as cube:
        # go
        await cube.api.motor.motor_control(10, -10)
        await asyncio.sleep(2)
        # stop
        await cube.api.motor.motor_control(0, 0)

    return 0

if __name__ == "__main__":
    asyncio.run(motor_1())
```

### Motor control (move to specified position)

Use `motor.motor_control_target()` to move the cube to a specified position on the mat.

```Python
import asyncio

from toio import *

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))

async def motor_2():
    async with ToioCoreCube() as cube:
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

if __name__ == "__main__":
    asyncio.run(motor_2())
```
### Motor control (move to multiple specified positions)

Use `motor.motor_control_multiple_targets()` to move the cube to a specified position on multiple mats.

```Python
import asyncio

from toio import *

async def motor_3():
    async with ToioCoreCube() as cube:
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

if __name__ == "__main__":
    asyncio.run(motor_3())
```

### Multiple cubes control

This is an example of `MultipleToioCoreCubes()`.

`cubes=` parameter is the number of cubes to use.

`MultipleToioCoreCubes()` is a context manager.
In the `async with` block, cubes are already connected and
all cubes are disconnected when exiting `async with` block.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    async with MultipleToioCoreCubes(cubes=2) as cubes:
        await cubes[0].api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0xFF, g=0x00, b=0xFF))
        )
        await cubes[1].api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0xFF))
        )
        await asyncio.sleep(3)

    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

#### Name the cubes and access them by name

If `name=` parameter is given to `MultipleToioCoreCubes()`, each cube can be accessed by name.

```Python
import asyncio

from toio import *

async def scan_and_connect():
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        await cubes.taro.api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0xFF, g=0x00, b=0xFF))
        )
        await cubes.jiro.api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0xFF))
        )
        await asyncio.sleep(3)

    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

Accessing by class properties may not be understood by LSP or code completion systems.
Therefore, it can be written using `named()` as follows:

```Python
import asyncio

from toio import *

async def scan_and_connect():
    async with MultipleToioCoreCubes(cubes=2, names=("taro", "jiro")) as cubes:
        await cubes.named("taro").api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0xFF, g=0x00, b=0xFF))
        )
        await cubes.named("jiro").api.indicator.turn_on(
            IndicatorParam(duration_ms=0, color=Color(r=0x00, g=0xFF, b=0xFF))
        )
        await asyncio.sleep(3)

    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```


