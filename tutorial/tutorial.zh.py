# %% [markdown]
# #toio.py基础程序教程 (v1.0)
'''
在本教程中，我们将使用toio.py创建一个程序。
该程序最终将会实现将第一个Q宝随机放置到活动用操作垫上，第二个Q宝会自动获取第一个Q宝的坐标，并自动移动到第一个Q宝的位置。

使用前需要准备以下内容：
1.	2台Q宝机器人。
2.	活动用操作垫。
3.	配置好toio.py的Visual Studio Code编程软件。

注意：本教程是为具有Python基础知识的人准备的。这里没有对Python语法以及基本用法的讲解。
'''

# --------------------------------------------------------------------------------
# %% [markdown]
## 检测是否安装所需的软件包
'''
在 Visual Studio Code 代码单元中执行以下脚本。

要运行单元格代码，请单击 Visual Studio Code 中标记为“运行单元格”的区域。
本教程使用单元格来测试功能。
确保您已经掌握了如何执行单元格代码。
'''

!pip install setuptools --upgrade
!pip install toio-py --upgrade
!pip install bleak
!pip install ipykernel

# --------------------------------------------------------------------------------
# %% [markdown]

'''
检查运行环境，找到以下的代码，并点击运行单元格。
如果反馈结果显示 “OK”，那么所需的软件已经正确安装。
'''

import sys

print(
    "Python version (%d.%d) : " % (sys.version_info.major, sys.version_info.minor),
    end="",
)
if sys.version_info.major == 3 and sys.version_info.minor >= 11:
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
# # 扫描Q宝程序
'''
本节内容讲解如何调用BLEScanner.scan()方法，来识别和扫描Q宝。

使用示例和介绍
dev_list = await BLEScanner.scan(num=10, sort="rssi", timeout=5)
	参数说明：
 	num 		- 		扫描最多10个Q宝并查看结果
 	sort 		- 		结果按照RSSI进行排序
 	timeout 		- 		超时时间为5秒

 	说明：由于“scan()”是一个异步函数，所以使用“await”来等待它们完成。

 	打开Q宝电源，点击上面的“运行单元格”，查看扫描的Q宝信息。
'''

from toio.scanner import BLEScanner

dev_list = await BLEScanner.scan(num=10, sort="rssi", timeout=5)
for n, ble_device in enumerate(dev_list):
    print(f"\ncube: {n + 1} ----------\n")
    print(ble_device)


# --------------------------------------------------------------------------------
# %% [markdown]
# # 生成ToioCoreCube对象
'''
完成Q的扫描后，接下来需要创建对象才能完成对Q宝的控制。本节内容讲解如何生成ToioCoreCube()对象。
使用示例和介绍
    	cube = ToioCoreCube(dev_list[0].interface)

使用设备信息的接口（CubeInfo）生成一个新的ToioCoreCube示例。从扫描结果中获得一个参数。

如果你运行它并出现以下信息，你就成功生成了一个示例。（其中 `0X??????????????????`部分包含了18个十六进制字符）
此时需要注意的上述图片仅供参考，每个Q宝都有一个独立的数值。
'''

from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube

dev_list = await BLEScanner.scan(num=1)
if len(dev_list) > 0:
    cube = ToioCoreCube(dev_list[0].interface)
    print(cube)
else:
    print("No cubes found")


# --------------------------------------------------------------------------------
# %% [markdown]
# # 连接与断开
'''
本节内容讲解如何使用ToioCoreCube.connect()和ToioCoreCube.disconnect()方法连接与断开Q宝。

使用示例和介绍
    		await cube.connect()
   		 	await cube.disconnect()

 仅通过生成ToioCoreCube的示例，仍然无法实现与Q宝的通信。我们可以在程序中调用“connect()”，以实际连接到Q宝，并允许它进行通信。需要断开连接时，请在“cube”上调用“disconnect()”即可断开与Q宝的连接。

 	说明：connect()和disconnected()是异步函数, 所以使用“await”来等待它们完成。

以下代码将连接到立方体并在1秒后断开连接。
'''


import asyncio

from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube

dev_list = await BLEScanner.scan(num=1)
if len(dev_list) > 0:
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()
    print("Connected")
    await asyncio.sleep(1)
    await cube.disconnect()
    print("Disconnected")
else:
    print("No cubes found")


# --------------------------------------------------------------------------------
# %% [markdown]
# # 访问每个Q宝的功能
'''
通过上述操作，现在可以扫描、连接和断开Q宝。接下来，我们将控制Q宝的各种功能。

 在实际控制功能之前，给大家介绍一下如何用toio.py访问功能。
 “ToioCoreCube”类有一个“api”子类。所有需要控制Q宝功能的类和函数都在这个“api”子类如下。
  ToioCoreCube.api
 “ToioCoreCube.api”类是一个接口类的集合，用于访问Q宝的各种功能。

说明：“ToioCoreCube.api.version” 这是toio.py支持的API的版本。关于API的版本和功能支持，见[toio Core Cube技术规范](https://toio.github.io/toio-spec/en/)

使用示例和介绍
ToioCoreCube.api.(输入接口类名称)

该方法用于访问各种功能的接口类。关于每个接口类的功能，请参考每个类的DocString。

 接口类的例子如下：
 - id_information: 处理ID读取功能的类
 - indicator: 控制Q宝的斜面的类
 - motor: 控制Q宝上的马达的类

		通过items()方法实现目前Q宝所有功能接口的查询。

'''


from toio.cube import ToioCoreCube
from toio.cube.api.base_class import CubeCharacteristic

cube = ToioCoreCube(None)
for key, value in vars(cube.api).items():
    if isinstance(value, CubeCharacteristic):
        print(f"{key:20s}: <interface class>")
    else:
        print(f"{key:20s}: {value}")


# --------------------------------------------------------------------------------
# %% [markdown]
# # 接口类
'''
本节将会介绍用于访问各种功能的接口类有一些共同的方法。

常见的静态方法：
  	is_my_data(data:bytearray)

 每个接口类都有一个“is_my_data(data:bytearray)”静态方法。“is_my_data()”如果是自己的特征读取或通知数据，则返回其参数对应的对象，否则返回“None”。

 普通方法：
注册通知处理函数
  	register_notification_handler(handler: CubeNotificationHandler)

取消注册通知处理程序函数
  	unregister_notification_handler(handler: CubeNotificationHandler)

'''

# --------------------------------------------------------------------------------
# %% [markdown]
# # 读取 ID
'''
本章节将会介绍使用“ToioCoreCube.api.id_information.read()”读取活动用操作垫的ID值。

 使用示例和介绍
    read_data = await cube.api.id_information.read()

“read_data”可以是以下返回值之一或“None”:如果“read_data”不符合以下任何返回值的格式, “read()”的返回值将默认为“None”
 （“id_information.read()”内部调用特征静态方法“IdInformation.is_my_data()”）

以下为“id_information.read()”的返回值：
 - PositionId
 - StandardId
 - PositionIdMissed
 - StandardIdMissed

由于“id_information.read()”会有返回值，下面我们将对这几个返回值进行详细的介绍。
'''
#
# #### 位置ID
#
# 这个返回值表示Q宝已经检测到一个位置ID。
#
# 位置ID属性
#
# | 属性              | 类型                                            |
# | ---------------- | ------------ | -------------------------------- |
# | 中心              | CubeLocation | Q宝的中心位置      |
# | 传感器            | CubeLocation | ID传感器在Q宝中的位置   |
#
# #### 标准Id
#
# 这个返回值表示Q宝已经检测到一个标准ID。
#
# 标准ID属性
#
# | 属性              | 类型         |                                  |
# | ---------------- | ------------ | -------------------------------- |
# | 值                | int          | 标准ID类型                         |
# | 角度              | int          | Q宝的角度                          |
#
# #### PositionIdMissed
# 是ToioCoreCube库中的一个常量，表示在没有检测到位置ID的情况下尝试执行了与立方体位置相关的操作。
#
# #### StandardIdMissed
# 是ToioCoreCube库中的一个常量，表示在没有检测到标准ID的情况下尝试执行了与标准ID相关的操作。
#
# 下面的代码执行了“id_information.read()”200次，并显示了读取的内容。


from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube

device_list = await BLEScanner.scan(1)
assert len(device_list)
cube = ToioCoreCube(device_list[0].interface)
await cube.connect()
print("start")
for n in range(200):
    read_data = await cube.api.id_information.read()
    if read_data is not None:
        print(n, type(read_data), read_data)
print("end")
await cube.disconnect()


# --------------------------------------------------------------------------------
# %% [markdown]
# # 通过通知程序读取ID
'''
本章节将会介绍 ToioCoreCube.api.id_information.register_notification_handler()和ToioCoreCube.api.id_information.unregister_notification_handler()的使用方法。

使用示例和介绍
    await cube.api.id_information.register_notification_handler(handler)
    await cube.api.id_information.unregister_notification_handler(handler)

通过上节的内容讲解，使用“ToioCoreCube.api.id_information.read()”可以获取Q宝在活动用操作垫上的实时数据。
在使用“read()”获得的数据是Q宝在执行时的实时数据，“read()”只提供最新的数据, 所以多次尝试“read()”并不能获得每次调用之间的信息变化。
Q宝自身拥有一个通知功能，可以主动发送检测ID信息。通过设置通知处理函数，可以使Q宝检测到的信息在Python端无遗漏地被接收。

注册通知处理函数：
“register_notification_handler()”

取消注册通知处理函数
“unregister_notification_handler()”

通知处理函数
在通知处理函数中，只有一个 “bytearray”的参数，此参数没有返回值。通知处理函数可以是同步的，也可以是异步的。如果通知处理函数为异步函数时, 该函数需要配合“await”一起使用。
通知处理函数的参数是以字节为单位从Q宝通知的数据。

下面的代码示例在id_information中注册了一个通知处理函数，然后在10秒内接收来自Q宝的通知并显示。

'''


import asyncio

from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube, IdInformation

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(str(id_info))

dev_list = await BLEScanner.scan(1)
assert len(dev_list)
cube = ToioCoreCube(dev_list[0].interface)
await cube.connect()
print("start")
await cube.api.id_information.register_notification_handler(notification_handler)
await asyncio.sleep(10)
await cube.api.id_information.unregister_notification_handler(
    notification_handler
)
print("end")
await cube.disconnect()


# --------------------------------------------------------------------------------
# %% [markdown]
# # 电机控制
'''
本章节将会介绍使用“ToioCoreCube.api.motor.motor_control()”控制Q宝的电机进行移动。

使用示例和说明
    await cube.api.motor.motor_control(10, 10)
    await cube.api.motor.motor_control(0, 0)
    await cube.api.motor.motor_control(50, -50, 1000)

通过指定左边和右边的电机速度来移动Q宝。该函数一共由三个参数组成，第三个参数是可选的，用于指定电机驱动时间。它的单位是毫秒[ms]。(如果你想运行1秒，则指定1000)

下面的代码以10的速度向前移动Q宝2秒，然后以50的速度旋转1秒。

'''

import asyncio

from toio.scanner import BLEScanner
from toio.cube import ToioCoreCube

dev_list = await BLEScanner.scan(1)
assert len(dev_list)
cube = ToioCoreCube(dev_list[0].interface)
await cube.connect()
print("go forward")
await cube.api.motor.motor_control(10, 10)
await asyncio.sleep(2)
print("stop")
await cube.api.motor.motor_control(0, 0)
print("spin turn (1000[ms])")
await cube.api.motor.motor_control(50, -50, 1000)
await asyncio.sleep(2)
print("end")
await cube.disconnect()

# --------------------------------------------------------------------------------
# %% [markdown]
# # 电机控制（移动到指定位置）
'''
本章节将会介绍使用“ToioCoreCube.api.motor.motor_control_target()”让Q宝在活动用操作垫上移动到指定位置。

使用示例和说明
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

将Q宝移动到活动用操作垫的指定坐标。

注：timeout参数	-	超时时间
指定超时时间。单位是秒[s]。如果指定为0，超时时间为10秒，不能指定0秒的超时时间。

'''
#
# ### 运动类型
#
#指定运动类型.
#
# | 值                                | 描述                                           |
# | --------------------------------- | ---------------------------------------------- |
# | MovementType.Curve                | 旋转时移动                                       |
# | MovementType.CurveWithoutReverse  | 在旋转中移动（不向后移动）                          |
# | MovementType.Linear               |移动后在旋转                                       |
#
# ### 速度
#
# 指定速度参数。速度参数由“max”和“speed_change_type”组成。
#
# #### max
# 指定最大的最高速度。速度可以在0到255的范围内指定。
#
# #### speed_change_type
# 指定速度变化类型。
#
# | 值                                           | 描述                                   |
# | ------------------------------------------- | -------------------------------------|
# | SpeedChangeType.Constant                    | 速度常数                              |
# | SpeedChangeType.Acceleration                | 逐渐加速向目标点移动                    |
# | SpeedChangeType.Deceleration                | 逐渐减速向目标点移动                    |
# | SpeedChangeType.AccelerationAndDeceleration | 逐渐加速到目标点一半，然后逐渐减速到目标点   |
#
# ### 目标
# 指定目标位置参数。目标位置参数由“cube_location”和“rotation_option”组成。
#
# #### Q宝位置
# 指定Q宝的位置信息。Q宝的位置信息由“Point”和“angle”组成。
#
# ##### 点
# 通过X、Y指定Q宝坐标
#
# ##### 角度
# 指定Q宝的角度，范围在0~360°之间。
#
# #### rotation_option
#指定关于Q宝在目标位置的角度的额外信息。
#
# | 值                              |角度                              | 旋转方向                  |
# | --------------------------------| ------------------------------- | ------------------------------------- |
# | RotationOption.AbsoluteOptimal  | 绝对角度                        | 旋转量最小方向              |
# | RotationOption.AbsolutePositive | 绝对角度                        | 正方向                    |
# | RotationOption.AbsoluteNegative | 绝对角度                        | 反方向                    |
# | RotationOption.RelativePositive | 相对角度                        | 正方向                    |
# | RotationOption.RelativeNegative | 相对角度                        | 反方向                    |
# | RotationOption.WithoutRotation  | (没有指定角度)                   | 没有旋转                  |
# | RotationOption.SameAsWriting    | (与写操作相同)                   | 旋转量最小方向             |
#
# 下面的代码将把Q宝移动到开发者操作垫上坐标为(200, 200)的位置。移动的结果是通过通知处理函数获得的。请将Q宝放在活动用垫子上后运行它。


import asyncio
from toio import *

def notification_handler(payload: bytearray):
    motor_info = Motor.is_my_data(payload)
    print(type(motor_info), str(motor_info))

dev_list = await BLEScanner.scan(1)
assert len(dev_list)
cube = ToioCoreCube(dev_list[0].interface)
await cube.connect()
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
await cube.disconnect()


# --------------------------------------------------------------------------------
# %% [markdown]
# # 控制两台Q宝
'''
本章节我们的目标是通过结合现有的功能来完成这个任务。扫描两个Q宝并连接它们。
通过程序，让第一个Q宝的LED灯变为绿色，并注册一个通知处理函数来读取坐标信息。
如果来自Q宝的通知是一个位置ID，那么将Q宝中心的坐标存储在全局变量“green_cube_location”中。
同时，让第二个Q宝上的灯变成红色并旋转1秒。 在第二个Q宝连接10秒后, 与所有Q宝断开连接并退出。

'''

import asyncio
from toio import *


green_cube_location = None

def id_notification_handler(payload: bytearray):
    global green_cube_location
    id_info = IdInformation.is_my_data(payload)
    if isinstance(id_info, PositionId):
        green_cube_location = id_info.center
        print(str(green_cube_location))

dev_list = await BLEScanner.scan(2)
assert len(dev_list) == 2
cube_1 = ToioCoreCube(dev_list[0].interface)
cube_2 = ToioCoreCube(dev_list[1].interface)

print("connect cube_1")
await cube_1.connect()
print("connect cube_2")
await cube_2.connect()

red = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 255, g = 0, b = 0)
)

green = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 0, g = 255, b = 0)
)
await cube_1.api.indicator.turn_on(green)
await cube_2.api.indicator.turn_on(red)

print("start")
await cube_1.api.id_information.register_notification_handler(id_notification_handler)
await cube_2.api.motor.motor_control(30, -30, 1000)

await asyncio.sleep(10)

await cube_1.api.id_information.unregister_notification_handler(
    id_notification_handler
)
print("end")
await cube_1.disconnect()
await cube_2.disconnect()


# --------------------------------------------------------------------------------
# %% [markdown]
# # 进阶教学程序一
'''
将第二个Q宝的移动方式从简单的电机控制改为移动到指定坐标。
第二个Q宝的目标位置是在第一个Q宝的通知处理器中获得的坐标。
该坐标通过全局变量“green_cube_location”共享。
'''

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

dev_list = await BLEScanner.scan(2)
assert len(dev_list) == 2
cube_1 = ToioCoreCube(dev_list[0].interface)
cube_2 = ToioCoreCube(dev_list[1].interface)

print("connect cube_1")
await cube_1.connect()
print("connect cube_2")
await cube_2.connect()

red = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 255, g = 0, b = 0)
)

green = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 0, g = 255, b = 0)
)
await cube_1.api.indicator.turn_on(green)
await cube_2.api.indicator.turn_on(red)

print("start")
await cube_1.api.id_information.register_notification_handler(id_notification_handler)
await cube_2.api.motor.register_notification_handler(motor_notification_handler)

for _ in range(30):
    if green_cube_location is not None and red_cube_arrived:
        red_cube_arrived = False
        print("cube_2: move to", str(green_cube_location))
        await cube_2.api.motor.motor_control_target(
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

await cube_2.api.motor.unregister_notification_handler(
    motor_notification_handler
)
await cube_1.api.id_information.unregister_notification_handler(
    id_notification_handler
)
print("end")
await cube_1.disconnect()
await cube_2.disconnect()



# --------------------------------------------------------------------------------
# %% [markdown]
# # 进阶教学程序二
'''
运行控制多个Q宝的程序时，会出现依次连接和断开Q宝的情况，为了可以更好的解决这个问题，我们可以使用“asyncio.gather()”。
通过 “asyncio.gather()”，可以同时等待多个异步操作（可以让多个Q宝同时连接和断开）。
下面的代码经过修改，可以同时连接到Q宝，打开灯并断开连接。
'''


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

dev_list = await BLEScanner.scan(2)
assert len(dev_list) == 2
cube_1 = ToioCoreCube(dev_list[0].interface)
cube_2 = ToioCoreCube(dev_list[1].interface)

print("connect cubes")
await asyncio.gather(cube_1.connect(), cube_2.connect())

red = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 255, g = 0, b = 0)
)

green = IndicatorParam(
    duration_ms = 0,
    color = Color(r = 0, g = 255, b = 0)
)

await asyncio.gather(cube_1.api.indicator.turn_on(green), cube_2.api.indicator.turn_on(red))

print("start")
await cube_1.api.id_information.register_notification_handler(id_notification_handler)
await cube_2.api.motor.register_notification_handler(motor_notification_handler)

for _ in range(30):
    if green_cube_location is not None and red_cube_arrived:
        red_cube_arrived = False
        print("cube_2: move to", str(green_cube_location))
        await cube_2.api.motor.motor_control_target(
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

await cube_2.api.motor.unregister_notification_handler(
    id_notification_handler
)
await cube_1.api.id_information.unregister_notification_handler(
    id_notification_handler
)
print("end")
await asyncio.gather(cube_1.disconnect(), cube_2.disconnect())



# --------------------------------------------------------------------------------
# %% [markdown]
# # 教程结束
'''
感谢您的阅读。以上部分为本教程的全部教学内容。
本教程的讲解代码请参考示例目录中的“tutorial_pursuer.py”，这部分代码可以作为一个单独的程序来执行，而不是作为一个代码单元格的函数。
'''

# 在示例目录下有几个额外的示例程序。
# 下一步，你可能想尝试自己修改示例程序。
# ## 示例程序的列表
#
# | Example                      | Description                             |
# | ---------------------------- | --------------------------------------- |
# | examples/detect_mat.py       | 读取坐标并显示垫子类型                      |
# | examples/motor_control.py    | 控制电机                                 |
# | examples/read_id.py          | 读取ID值信息                              |
# | examples/scan_and_connect.py | 扫描和连接                                |
# | examples/tutorial_pursuer.py | 本教程最终代码                             |

# --------------------------------------------------------------------------------
# %% [markdown]
# # 补充信息 - 如何在不使用代码单元格的情况下执行异步处理
'''
在编写异步处理程序时，需要注意以下几点：
I.	不使用代码单元功能的异步处理，例如 toio.py。
II.	“await”只能在异步函数中使用。(可以直接用代码单元格函数来调用)
III.	当使用像toio.py这样的异步处理时，首先要创建一个异步函数，然后用“asyncio.run()”执行该异步函数。
'''
#
# **例如：一个简单的Python程序，执行异步处理**
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
