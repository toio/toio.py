# %% [markdown]
# # toio.py チュートリアル (v1.1)
#
# このチュートリアルでは、toio.py を使ったプログラムを作ります。
# プログラムは、一つのキューブをマットの上に置くと、もう一つのキューブが
# 置かれたキューブに寄ってくるという動作をします。
#
# キューブ２個と開発者用マットを使います。
#
# このチュートリアルは Visual Studio Codeの [コードセル機能](https://code.visualstudio.com/docs/python/jupyter-support-py#_jupyter-code-cells)
# を使って実際に動きを確認できます。
#
# このチュートリアルはPythonの基礎的知識を持っている人を対象としています。
# Pythonの文法や基本的な使い方などについての説明はありません。
#


# --------------------------------------------------------------------------------
# %% [markdown]
# ## 必要となるパッケージのインストール
#
# 下記のスクリプトを VSCode のコードセルで実行します。
#
# コードセルを実行するには、VSCode上で `Run Cell` と表示されている部分をクリックします。
# このチュートリアルではコードセルを使って動作確認を行います。
# ここでコードセルの実行方法をマスターしておいてください。


!pip install setuptools --upgrade
!pip install typing-extensions
!pip install bleak
!pip install toio-py --upgrade
!pip install ipykernel


# %% [markdown]
# ## 環境の確認
#
# 下記のスクリプトをVSCodeのコードセルで実行します。
#
# すべて `OK` と表示されれば必要なソフトウェアが正しくインストールできています。
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
# # キューブのスキャン、接続、切断
#
# ## ToioCoreCube.scan()
# ## ToioCoreCube.connect()
# ## ToioCoreCube.disconnect()
#
# 使用例と説明
# ```Python
#    await cube.scan()
#    await cube.connect()
#    await cube.disconnect()
# ```
#
# ToioCoreCubeのインスタンスを生成し、キューブのスキャン、接続、切断を行います。
# `cube` の `scan()` を呼び出した後に `connect()` を呼び出してキューブと接続し
# 通信が行えるようにします。
#
# 切断するときは `cube` の `disconnect()` を呼び出します。
#
# `scan()`、`connect()`、`disconnect()` は非同期関数なので `await` で完了を待ちます。
#
# 下記のコードはキューブと接続し、1秒後に切断します。

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
# # コンテキストマネージャによるキューブのスキャン、接続、切断
#
# ## ToioCoreCube()
#
# 使用例と説明
# ```Python
#    async with ToioCoreCube()
# ```
#
# ToioCoreCube クラスはコンテキストマネージャなので、`async with` 文を使うことで
# キューブのスキャン、接続、切断を簡単に行うことができます。
#
# 下記のコードはキューブと接続し、1秒後に切断します。

import asyncio

from toio.cube import ToioCoreCube

async with ToioCoreCube() as cube:
    print("Connected")
    await asyncio.sleep(1)
print("Disconnected")

# --------------------------------------------------------------------------------
# %% [markdown]
# # 複数のキューブのスキャン、接続、切断
#
# ## MultipleToioCoreCubes()
#
# 使用例と説明
# ```Python
#    async with MultipleToioCoreCubes()
# ```
#
# MultipleToioCoreCubes クラスを使うことで、複数のキューブに対してのスキャン、
# 接続、切断を行うことができます。
# MultipleToioCoreCubes クラスは ToioCoreCube クラスと同様にコンテキストマネージャなので
# `async with` 文を使うことでキューブのスキャン、接続、切断を簡単に行うことができます。
#
# 下記のコードは2台のキューブと接続し、1秒後に切断します。

import asyncio

from toio.cube.multi_cubes import MultipleToioCoreCubes

async with MultipleToioCoreCubes(cubes=2) as cubes:
    print("Connected to %s" % cubes[0].name)
    print("Connected to %s" % cubes[1].name)
    await asyncio.sleep(1)
print("Disconnected")


# --------------------------------------------------------------------------------
# %% [markdown]
# # キューブの各機能へのアクセス
#
# キューブのスキャン、接続、切断ができるようになりました。
# 次はキューブが持つ各種機能の制御を行います。
#
# 実際に機能制御を行う前に、toio.py でどのように機能にアクセスするのか、
# その概要を説明します。
#
# `ToioCoreCube` クラスは `api` サブクラスを持っています。
# キューブの機能制御を行うクラスや関数は、この `api` サブクラス以下に集約されています。
#
# ## ToioCoreCube.api
#
# `ToioCoreCube.api` クラスはキューブの各種機能にアクセスするためのインターフェースクラスを
# 集めたクラスです。
#
# ### ToioCoreCube.api.(インターフェースクラス名)
#
# 各種機能にアクセスするためのインターフェースクラスです。
#
# インターフェースクラスは[技術仕様書のキャラクタリスティック](https://toio.github.io/toio-spec/en/docs/ble_communication_overview#using-the-cubes-functions)
# ごとに作られています。
# 各インターフェースクラスが持つ機能については、各クラスのDocStringを参照してください。
#
# インターフェースクラスの例
#
# - id_information: IDの読み出し機能を扱うクラス
# - indicator: キューブのランプを制御するクラス
# - motor: キューブのモーターを制御するクラス
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
# ## インターフェースクラス
#
# 各種機能にアクセスするためのインターフェースクラスは、いくつかの共通したメソッドを持ちます。
#
# ### 共通のスタティックメソッド
#
# #### `is_my_data(data: bytearray)`
#
# 各キャラクタリスティクに対応するインターフェースクラスは
# `is_my_data(data: bytearray)` スタティックメソッドを持ちます。
# `is_my_data()` は、引数のデータが自キャラクタリスティクの読み出しまたは通知データの
# 場合にはデータに対応するオブジェクトを返し、それ以外では `None` を返します。
#
# ### 共通のメソッド
#
# #### `register_notification_handler(handler: CubeNotificationHandler)`
#
# 通知ハンドラ関数（後述）を登録します。
#
# #### `unregister_notification_handler(handler: CubeNotificationHandler)`
#
# 通知ハンドラ関数（後述）を登録解除します。
#


# --------------------------------------------------------------------------------
# %% [markdown]
# # IDの読み出し
#
# ## ToioCoreCube.api.id_information.read()
#
# 使用例と説明
# ```Python
#    read_data = await cube.api.id_information.read()
# ```
#
# [ID Information キャラクタリスティク](https://toio.github.io/toio-spec/en/docs/ble_id)からの読み出しを行います。
#
# 'read_data' は下記いずれかのオブジェクトまたは `None` です。
# 'read_data' が下記に示されるどのオブジェクトのフォーマットとも一致しない場合、`read()` の返値は `None` になります。
#
# （`id_information.read()` は内部でキャラクタリスティクのスタティックメソッド `IdInformation.is_my_data()` を呼び出しています）
#
# - PositionId
# - StandardId
# - PositionIdMissed
# - StandardIdMissed
#
# ### `id_information.read()` が返すオブジェクト
#
# #### PositionId
#
# キューブがPosition IDを検出したことを表すオブジェクトです。
#
# PositionId のアトリビュート
#
# | アトリビュート名 | 型           |                                  |
# | ---------------- | ------------ | -------------------------------- |
# | center           | CubeLocation | キューブの中心位置座標           |
# | sensor           | CubeLocation | キューブの読み取りセンサ位置座標 |
#
# #### StandardId
#
# キューブがStandard IDを検出したことを表すオブジェクトです。
#
# StandardId のアトリビュート
#
# | アトリビュート名 | 型           |                                  |
# | ---------------- | ------------ | -------------------------------- |
# | value            | int          | Standard IDの種類                |
# | angle            | int          | キューブの角度                   |
#
# #### PositionIdMissed
#
# キューブが Position ID の上から取り除かれたことを表すオブジェクトです。
#
# #### StandardIdMissed
#
# キューブが Standard ID の上から取り除かれたことを表すオブジェクトです。
#
# 下記コードは `id_information.read()` を200回行い、読み出した内容を表示します。

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
# # 通知ハンドラ関数によるIDの読み出し
#
# ## ToioCoreCube.api.id_information.register_notification_handler()
# ## ToioCoreCube.api.id_information.unregister_notification_handler()
#
# 使用例と説明
# ```Python
#    await cube.api.id_information.register_notification_handler(handler)
#    await cube.api.id_information.unregister_notification_handler(handler)
# ```
#
# `read()` で得られる情報は、`read()`を行ったタイミングでキューブが持っている情報です。
# `read()` では直近の情報しか得られないため、複数回 `read()` を行ったとしても、各呼び出しの間に変化した情報を得られません。
#
# キューブには通知機能があり、検知した情報を自発的に送信します。
# 通知ハンドラ関数を設定することにより、キューブが検出した情報を漏らさずPython側で受け取れます。
#
# `register_notification_handler()` は通知ハンドラ関数を登録します。
# `unregister_notification_handler()` は通知ハンドラ関数を登録解除します。
#
# ## 通知ハンドラ関数
#
# 通知ハンドラ関数は `bytearray` を引数に取り、返値を持ちません。
#
# 通常の関数だけでなく非同期関数もハンドラ関数として使えます。
# 通知ハンドラ関数が非同期関数の場合、通知ハンドラ関数は内部で `await` を使用した処理を実行することができます。
#
# 通知ハンドラ関数の引数はキューブから通知されたバイト列のデータです。
#
# 下記コードは id_information にハンドラ関数を登録し、キューブからの通知を10秒間受けて表示します。
#

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
# # モーター制御
#
# ## ToioCoreCube.api.motor.motor_control()
#
# 使用例と説明
# ```Python
#    await cube.api.motor.motor_control(10, 10)
#    await cube.api.motor.motor_control(0, 0)
#    await cube.api.motor.motor_control(50, -50, 1000)
# ```
#
# 左右のモーター速度を指定してキューブを動かします。
#
# 第3引数はオプションで、モーターの駆動時間を指定します。単位はミリ秒[ms]です。
# （1秒間動かしたい場合は1000を指定します）
#
# 下記コードはキューブを速度10で2秒間前進させた後、速度50で1秒間回転させます。

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
# # モーター制御（指定位置へ移動）
#
# ## ToioCoreCube.api.motor.motor_control_target()
#
# 使用例と説明
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
# マット上の指定した座標へキューブを移動させます。
#
# ## 引数
#
# ### timeout
#
# タイムアウト時間を指定します。単位は秒[s]です。
# 0 を指定した場合、タイムアウト時間は 10 秒になります。
# タイムアウト時間 0 秒は指定できません。
#
# ### movement_type
#
# 移動タイプを指定します。
#
# | 値                                | 説明                         |
# | --------------------------------- | ---------------------------- |
# | MovementType.Curve                | 回転しながら移動             |
# | MovementType.CurveWithoutReverse  | 回転しながら移動（後退なし） |
# | MovementType.Linear               | 移動してから回転             |
#
# ### speed
#
# スピードパラメータを指定します。
#
# スピードパラメータは `max` と `speed_change_type` で構成されます。
#
# #### max
#
# 最高スピードを指定します。スピードは 0 から 255 の範囲で指定します。
#
# #### speed_change_type
#
# 速度変化タイプを指定します。
#
# | 値                                          | 説明                                               |
# | ------------------------------------------- | -------------------------------------------------- |
# | SpeedChangeType.Constant                    | 速度一定                                           |
# | SpeedChangeType.Acceleration                | 目標地点まで徐々に加速                             |
# | SpeedChangeType.Deceleration                | 目標地点まで徐々に減速                             |
# | SpeedChangeType.AccelerationAndDeceleration | 中間地点まで徐々に加速し、そこから目標地点まで減速 |
#
# ### target
#
# 目標位置パラメータを指定します。
#
# 目標位置パラメータは `cube_location` と `rotation_option` で構成されます。
#
# #### cube_location
#
# キューブの位置情報を指定します。
#
# キューブの位置情報は `Point` と `angle` で構成されます。
#
# ##### Point
#
# キューブの座標を `x` `y` で指定します。
#
# ##### angle
#
# キューブの角度を指定します。 0 から 360 の間で指定します。
#
# #### rotation_option
#
# 目標地点でのキューブの角度に関する追加情報を指定します。
#
# | 値                              | 角度の意味           | 回転方向           |
# | --------------------------------| -------------------- | ------------------ |
# | RotationOption.AbsoluteOptimal  | 絶対角度             | 回転量が少ない方向 |
# | RotationOption.AbsolutePositive | 絶対角度             | 正方向             |
# | RotationOption.AbsoluteNegative | 絶対角度             | 負方向             |
# | RotationOption.RelativePositive | 絶対角度             | 正方向             |
# | RotationOption.RelativeNegative | 相対角度             | 負方向             |
# | RotationOption.WithoutRotation  | 角度指定なし         | 回転しない         |
# | RotationOption.SameAsWriting    | 書き込み時と同じ角度 | 回転量が少ない方向 |
#
# 下記コードはキューブを開発者マット上の座標 (200, 200)へ移動させます。
#
# 移動の結果は通知ハンドラ関数で取得します。
#
# キューブを開発者マットの上に置いてから実行させてください。

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
# # ふたつのキューブの制御
#
# 今までの機能を組み合わせて完成を目指します。
#
# ふたつのキューブをスキャンして接続します。
#
# ひとつめのキューブのランプを緑色に点灯させ、
# 通知ハンドラ関数を登録して座標情報を読み込むようにします。
# キューブからの通知が Position ID の場合は、キューブの中心座標を
# グローバル変数 `green_cube_location` に保存しておきます。
#
# ふたつめのキューブのランプは赤色に点灯させ、1 秒間回転させます。
#
# ふたつめのキューブが接続してから 10 秒後に全てのキューブとの通信を切断して終了します。

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
# # 完成
#
# ふたつめのキューブの移動方法を単純なモーター制御から指定座標への移動へ変更します。
#
# ふたつめのキューブの目標位置は、ひとつめのキューブの通知ハンドラで取得した座標です。
# 座標はグローバル変数 `green_cube_location` を介して共有します。
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
# # チュートリアル終了
#
# おつかれさまでした。チュートリアルはこれで完了です。
#
# このチュートリアルの完成コードをコードセル機能ではなく一つのプログラムとして実行できる
# ようにしたものが example ディレクトリの `tutorial_pursuer.py` です。
#
# 他にも example ディレクトリにはいくつかのサンプルプログラムがあります。
# 次のステップとして、サンプルプログラムを自分で改造してみるのもよいでしょう。
#
# ## サンプルプログラム一覧
#
# | サンプルプログラム           | 説明                                                         |
# | ---------------------------- | ------------------------------------------------------------ |
# | examples/detect_mat.py       | 読み取った座標から、使われているマットの種類を表示します     |
# | examples/motor_control.py    | モーター制御（移動、目標指定移動、複数目標指移動） |
# | examples/multi.py            | 複数台Cubeへのスキャンと接続 |
# | examples/read_position.py    | ID 読み取り                                          |
# | examples/scan_and_connect.py | スキャンと接続                                     |
# | examples/tutorial_pursuer.py | このチュートリアルで作成したプログラム（単独実行版）         |
# --------------------------------------------------------------------------------

# %% [markdown]
# # 補足情報：コードセルを使わない非同期処理の実行方法
#
# コードセル機能を使わないでtoio.pyのような非同期処理を扱うプログラムを
# 作るときには、いくつかの注意点があります。
#
# await は非同期関数内でしか使えません。（コードセル機能では直接呼び出せます）

# toio.pyのような非同期処理を使う場合は、まず非同期関数を作り、その非同期関数を
# `asyncio.run()` で実行します。
#
# **例：非同期処理を実行する簡単な Python プログラム**
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
