# toio.py

[![PyPI](https://img.shields.io/pypi/v/toio-py?color=00aeca)](https://pypi.org/project/toio-py/)

これは Python から[toio コアキューブ](https://toio.io/platform/cube/)を制御するためのライブラリです。

[toio コアキューブ技術仕様](https://toio.github.io/toio-spec/) v2.4.0 に基づいています。

## 特徴

- Bluetooth 通信に[bleak](https://github.com/hbldh/bleak)を使用
- Python 3.8 以降のバージョンをサポート （Python 3.12 の使用を推奨）
- マルチプラットフォーム (Windows, Linux, macOS, iOS, iPadOS)
- 専用のドングルが不要
- toio コアキューブ技術仕様に基づいた非同期 API (ToioCoreCube API) と 簡単にキューブを制御するための同期 API (SimpleCube API) の 2 種類を用意
- BLE アドレス、キューブ固有名を指定してのスキャン機能
- キャラクタリスティックごとに分類されたキューブ機能制御の API （ToioCoreCube API）
- ペアリング済みキューブのスキャン機能 (Windows のみ)

## 動作確認環境

### 主な確認環境

- Windows: Windows10 (21H2)

### 補助的な確認環境

- Linux: Ubuntu22.04
- macOS: macOS 13(Ventura)
- iOS, iPadOS: 17

## セットアップとチュートリアル

セットアップの方法とチュートリアルの実行については下記を参照してください。

- [セットアップガイド （日本語）](https://github.com/toio/toio.py/blob/main/SETUP_GUIDE.ja.md)
- [セットアップガイド （英語）](https://github.com/toio/toio.py/blob/main/SETUP_GUIDE.en.md)


---

## SimpleCube API

簡単に toio コアキューブを制御するための SimpleCube API に関する情報は[SIMPLE_API.ja.md](https://github.com/toio/toio.py/blob/main/SIMPLE_API.ja.md)を参照してください。

- [SIMPLE_API.ja.md （日本語）](https://github.com/toio/toio.py/blob/main/SIMPLE_API.ja.md)
- [SIMPLE_API.en.md （英語）](https://github.com/toio/toio.py/blob/main/SIMPLE_API.en.md)

---

## API ドキュメント

- [API ドキュメント](https://toio.github.io/toio.py/)

---


## toio.py 実装概要

toio.py は大きく分けて下記のクラスで構成されています。

### ToioCoreCube

キューブを制御するためのクラスです。

ToioCoreCube は[toio コアキューブ技術仕様](https://toio.github.io/toio-spec/) に記載されているキャラクタリスティックに対応したサブクラスを持ちます。このサブクラスを経由してキューブの各種機能へアクセスします。

#### v1.1 から追加された機能

ToioCoreCubeクラスは基本的な Scanner の機能を持ち、Scanner を使わなくてもキューブの探索と接続が行えるようになりました。  
複雑な設定でのキューブの探索には Scanner を使ってください。

### Scanner

BLE インターフェース経由でキューブを探索するためのクラスです。

キューブは以下の方法で検索することができます。

- 近くにあるキューブを探索
- 名前（toio コアキューブの末尾 3 桁）を指定して特定のキューブを探索

以下はWindowsとLinuxでのみ利用可能です。

- BLE アドレスを指定して特定のキューブを探索

以下はWindowsでのみ利用可能です。

- Windows に登録されている（ペアリングされている）キューブの探索

#### MultipleToioCoreCubes

このクラスは v1.1 から追加されました。

複数台のキューブ制御を簡単に行うための補助的なクラスです。

複数の ToioCoreCube クラスへの接続、切断制御を行います。

## サンプルコード

### キューブへの接続

パラメータなしで `ToioCureCube()` インスタンスを生成し、`scan()`, `connect()` を呼び出します。

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

`ToioCoreCube()` は非同期コンテキストマネージャなので `async with` を使うことでスキャン、接続、切断を暗黙に行えます。  
前述のコードは `async with` を使って下記のように書けます。

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

### Scanner を使ったスキャンと接続

`BLEScanner.scan()` を使います。

引数はスキャンで見つけるキューブの数です。

タイムアウト（デフォルト値は 5 秒）までに指定された数のキューブが見つからない場合は、タイムアウト時点で見つかった数のキューブのリストを返します。

以下のサンプルでは、近くにあるキューブをスキャンして接続します。

接続してから 3 秒後に切断します。

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan(num=1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0])
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Scanner を使ったスキャンと接続（キューブの名前を指定してスキャンする）

`BLEScanner.scan_with_id()` を使います。

引数はキューブ末尾 3 桁文字列の[set（集合型）](https://docs.python.org/ja/3/library/stdtypes.html?highlight=set#set-types-set-frozenset)です。
一台しかスキャンしない場合でも引数は set で与えます。

タイムアウト（デフォルト値は 5 秒）までに指定された数のキューブが見つからない場合は、タイムアウト時点で見つかったキューブのリストを返します。

```Python
    dev_list = await BLEScanner.scan_with_id(cube_id={"C7f"})
```

`toio Core Cube-C7f`をスキャンして接続します。

接続してから 3 秒後に切断します。

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan_with_id(cube_id={"C7f"})
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0])
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### Scanner を使ったスキャンと接続（ペアリング済みキューブをスキャンする：Windows のみサポート）

Windows のみ、ペアリング済みのキューブをスキャンすることができます。

`BLEScanner.scan_registered_cubes()`を使います。

引数はスキャンで見つけるキューブの数です。

タイムアウト（デフォルト値は 5 秒）までに指定された数のキューブが見つからない場合は、タイムアウト時点で見つかった数のキューブのリストを返します。

```Python
    dev_list = await BLEScanner.scan_registered_cubes()
```

ペアリング済みのキューブをスキャンして接続します。（実行する前に"Bluetooth デバイスの追加"で Windows とキューブをペアリングしておきます）

接続してから 3 秒後に切断します。

```Python
import asyncio

from toio import *

async def scan_and_connect():
    dev_list = await BLEScanner.scan_registered_cubes(num=1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0])
    await cube.connect()

    await asyncio.sleep(3)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
```

### キューブの位置情報取得

キューブの位置情報を取得するため、`ToioCoreCube.api.id_information` クラスを使います。
このクラスは[読み取りセンサーのキャラクタリスティック](https://toio.github.io/toio-spec/docs/ble_id)へのアクセスを行います。

下記コードはキューブの ID 情報を 200 回読み出して表示します。
`read()`を使うことにより、キャラクタリスティックへのリードを行います。

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

### キューブの位置情報取得（通知を使う）

`register_notification_handler()` で通知ハンドラを登録することにより、キューブからの通知を受け取ることができます。
通知は各キャラクタリスティックごとです。`ToioCoreCube.api.id_information.register_notification_handler()` で登録した通知ハンドラは
読み取りセンサーの通知だけを受け取ります。

下記のコードは通知により ID を読みだします。

10 秒後にハンドラを登録解除して切断します。

```Python
import asyncio

from toio import *

# 通知ハンドラ
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

Ctrl-C が押されるまで ID 情報を表示し続ける完全なコードは [examples/read_position.py](https://github.com/toio/toio.py/blob/main/examples/read_position.py) です。

### モーター制御

モーター制御には `ToioCoreCube.api.motor` クラスを使います。
このクラスは[モーターのキャラクタリスティック](https://toio.github.io/toio-spec/docs/ble_motor)へのアクセスを行います。

下記のコードは`motor_control()`を使ってキューブを 2 秒間その場で回転させます。

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

### モーター制御（指定位置まで移動）

`motor.motor_control_target()` を使ってキューブをマット上の指定位置まで動かします。

```Python
import asyncio

from toio import *

# 通知ハンドラ
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

### モーター制御（複数指定位置まで移動）

`motor.motor_control_multiple_targets()` を使ってキューブを複数のマット上の指定位置まで動かします。

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

### 複数台制御

`MultipleToioCoreCubes()` を使った複数台制御の例です。

`cubes=` パラメータで使用するキューブの数を指定します。

`MultipleToioCoreCubes()` はコンテキストマネージャです。
`async with` ブロック内ではキューブはすでに接続されています。
`async with` ブロックを出る時にすべてのキューブは切断されます。

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

`MultipleToioCoreCubes()` に `names=` パラメータを与えることにより、各キューブに名前でアクセスできます。

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

クラスプロパティを使った名前でのアクセスはLSPやコード補完システムに正しく理解されないことがあります。
そのため、`named()` を使って書くことができます。

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


