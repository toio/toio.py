# テスト

このドキュメントでは、テストの実行方法と各テストグループの内容を説明します。

## 必要条件

- Python 3.10 以降。Python 3.14 を推奨
- uv
- uv でインストールした開発用依存パッケージ
- hardware test を実行する場合は、実機の toio Core Cube

開発環境を同期します。

```bash
uv sync --dev
```

## 最小限のテスト実行

実機 cube を必要としない definition-level test を実行します。

```bash
uv run pytest tests/test_50_definition
```

これらのテストは fake や mock を使います。`tests/test_50_definition` だけを
指定した場合、テスト setup は実機 cube の探索を skip します。

## 全テスト実行

pytest の全テストを実行します。

```bash
uv run pytest
```

全テストには実機の toio Core Cube が必要なテストが含まれます。session 開始時に
`tests/conftest.py` が cube setup の prompt を表示し、近くの cube を scan して
`tests/_cubes.py` を生成することがあります。必要な cube の電源を入れてから続行
してください。既存の `tests/_cubes.py` を使う場合は、`s` を入力して Enter を押すと
再生成を skip できます。

hardware test の多くは test case 間に 3 秒待機します。これは BLE の状態がテスト間で
重なることを避けるための意図的な待機です。

## よく使うコマンド

1つの test file だけを実行します。

```bash
uv run pytest tests/test_50_definition/test_scanner.py
```

1つの test だけを実行します。

```bash
uv run pytest tests/test_50_definition/test_scanner.py::test_base_ble_scanner_strategy_quick_returns_early
```

log output を表示しながら実行します。

```bash
uv run pytest -s tests/test_50_definition
```

coverage を取得します。

```bash
uv run coverage run --source=toio -m pytest tests/test_50_definition
uv run coverage report
```

## テストグループ

### `tests/test_50_definition`

実機 cube を必要としない definition-level test です。

主な確認内容:

- mock した Bleak client を使った BLE connection state handling。
- configuration および indicator command の byte 生成と response の parse。
- `best` と `quick` の scanner strategy 動作と、cube initializer が受け付ける
  scanner のキーワード引数。
- `CubeInfo` からの `ToioCoreCube` 初期化。
- 姿勢角 notification の sensor payload dispatch。
- BLE hardware なしで確認できる definition や import-level の挙動。

CI やローカルでの regression check では、このテストグループを最初に実行するのが安全です。

### `tests/test_50_single_cube`

1台の cube を使う hardware test です。

主な確認内容:

- 1台の cube の connect / disconnect。
- battery、button、configuration、indicator、sound API。
- protocol version に関連する connection behavior。
- connection interval API。

少なくとも1台の電源が入った toio Core Cube が必要です。

### `tests/test_10_two_cubes`

2台の cube を使う hardware test です。

主な確認内容:

- 複数 cube がある場合の scanner behavior。
- `best` と `quick` の scan strategy とそのタイミング。
- RSSI と local name による sort。
- cube ID と BLE address による scan。
- scan 結果からの `ToioCoreCube` instance 作成。
- 対応環境での Windows registered-cube scan。

電源が入った toio Core Cube が2台必要です。Windows の registered-cube test では、
cube が OS に pair 済みである必要があります。

### `tests/test_50_mat`

toio mat を使う motor / movement test です。

主な確認内容:

- motor control。
- target movement。
- multiple-target movement。
- acceleration-based motor command。

これらのテストを実行する前に、必要な position ID mat の上に cube を置いてください。

#### mat test の実行

mat test 全体を実行します。

```bash
uv run pytest -s tests/test_50_mat
```

1つの file だけを実行します。

```bash
uv run pytest -s tests/test_50_mat/test_motor.py
uv run pytest -s tests/test_50_mat/test_motor_v1_2.py
```

1つの test だけを実行します。

```bash
uv run pytest -s tests/test_50_mat/test_motor.py::test_motor_2
```

準備 prompt が見えるように `-s` を付けて実行してください。これらの test は
`BLEScanner.scan(1)` で近くの cube を1台 scan するため、可能であれば対象 cube だけを
電源 ON にしてください。

#### mat test の準備

1. 電源が入った toio Core Cube を1台準備します。
2. test で使う座標を読み取れる position ID mat の上に cube を置きます。
3. `(120, 210)`, `(250, 170)`, `(350, 170)` の周辺を cube が移動できるようにします。
4. 対象 test を開始します。
5. cube setup で `tests/_cubes.py` の生成を求められた場合は、生成するなら Enter、
   既存 file を使うなら `s` を入力します。
6. `confirm` fixture を使う test では、cube を mat 上の安全な位置に置いてから Enter を押します。

`test_motor.py` と `test_motor_v1_2.py` は同じ動作を確認します。前者は
`TargetPosition`、`Speed`、enum value などの typed API value を使います。後者は同じ
motor command を tuple や integer form で指定します。

#### `test_motor_1`

target position は使いませんが、cube は移動します。

期待動作:

1. cube が接続されます。
2. 左右 motor が power `10` で約2秒動きます。
3. `motor_control(0, 0)` で左右 motor が停止します。
4. cube が切断されます。

短い直進動作をしても問題ない安全な場所で実行してください。

#### `test_motor_2`

position ID mat が必要です。`confirm` fixture を使います。

期待動作:

1. cube を position ID mat の上に置き、prompt で Enter を押します。
2. cube が接続され、motor notification handler が登録されます。
3. cube が coordinate `(350, 170)`、angle `0` に向かって linearly に移動します。
4. command は maximum speed `100`、acceleration and deceleration を使います。
5. test は約4秒待機し、motor を停止して切断します。
6. `ResponseMotorControlTarget` notification が `MotorResponseCode.SUCCESS` で返った場合のみ成功します。

cube が mat を読めない、開始位置が有効範囲外、移動が妨げられる、timeout 以内に target に
到達できない場合は、response が `SUCCESS` にならないことがあります。

#### `test_motor_3`

position ID mat が必要です。

期待動作:

1. cube を position ID mat の上に置きます。
2. cube が接続され、motor notification handler が登録されます。
3. cube が2つの target を linearly に移動します。
   - `(250, 170)`、angle `135`。
   - `(120, 210)`、angle `0`。
4. command は overwrite mode、maximum speed `100`、acceleration and deceleration を使います。
5. test は約5秒待機して切断します。
6. `ResponseMotorControlMultipleTargets` notification が `MotorResponseCode.SUCCESS` で返った場合のみ成功します。

開始位置から2つの target までの経路に障害物がないことを確認してください。

#### `test_motor_4`

前進できる十分なスペースがある安全な場所、または mat 上で実行してください。

期待動作:

1. cube が接続されます。
2. `motor_control_acceleration()` により、translation `100`、acceleration `5`、
   rotation velocity なし、forward direction、translational-velocity priority で動きます。
3. command duration は 2000 ms です。
4. test は約4秒待機して切断します。

この test は motor response notification を assert しません。cube が前進して停止することを確認してください。

### `tests/test_20_interactive`

手動確認や操作が必要な interactive hardware test です。

主な確認内容:

- indicator behavior。
- ID information notification。
- notification handler behavior。
- sensor と motion detection behavior。

一部のテストでは、観察した cube の挙動が正しいかどうかを operator が確認します。

#### interactive test の実行

interactive test 全体を実行します。

```bash
uv run pytest -s tests/test_20_interactive
```

ただし、sensor test の一部は多くの手動姿勢変更が必要なため、全体実行には時間がかかります。
通常の手動確認では、1つの file または1つの test だけを実行することを推奨します。

```bash
uv run pytest -s tests/test_20_interactive/test_indicator.py
uv run pytest -s tests/test_20_interactive/test_id_information.py::test_id_information_1
uv run pytest -s tests/test_20_interactive/test_sensor_v1_2.py::test_sensor_5
```

prompt や operator instruction が見えるように `-s` を付けて実行してください。
これらのテストは `BLEScanner.scan(1)` で近くの cube を1台 scan するため、可能であれば
対象 cube だけを電源 ON にしてください。

#### 共通の実施手順

1. 対象 cube の電源を入れます。
2. `uv run pytest -s ...` で対象 test を開始します。
3. cube setup で `tests/_cubes.py` の生成を求められた場合は、生成するなら Enter、
   既存 file を使うなら `s` を入力します。
4. `confirm` fixture を使う test では、cube や mat を準備してから prompt で Enter を押します。
5. 各 test の説明に従って手動操作を行います。
6. `get_result` fixture を使う test では、成功なら Enter、失敗なら `N` を入力して Enter を押します。

一部の test では cube button が中断条件です。手順で明示されていない限り、cube button は
押さないでください。

#### `test_indicator.py`

cube LED の目視確認を行う test です。各 test は `get_result` を使うため、最後の prompt で
観察結果を入力します。

- `test_indicator_turn_on`
  - 期待動作: LED が purple (`#FF0080`) で約2秒点灯し、その後消灯します。
- `test_indicator_turn_off_all`
  - 期待動作: LED が light green (`#00FF40`) で点灯し、約3秒後に `turn_off_all()` で消灯します。
- `test_indicator_turn_off`
  - 期待動作: LED が light green で点灯し、約3秒後に `turn_off(1)` で消灯します。
- `test_indicator_repeated_turn_on`
  - 期待動作: LED が light green と purple を 500 ms 間隔で5回繰り返し、その後消灯します。

#### `test_id_information.py`

`test_id_information_1` には position ID mat が必要です。

手順:

1. cube を position ID mat の上に置きます。
2. cube を下記の target area と向きに順番に移動します。
   - `x=98..141`, `y=142..185`, angle 約 `0` 度。
   - `x=356..399`, `y=142..185`, angle 約 `90` 度。
   - `x=356..399`, `y=314..357`, angle 約 `180` 度。
   - `x=98..141`, `y=314..357`, angle 約 `270` 度。
3. 各向きは約5度以内に合わせます。
4. すべての target area が検出されると test が終了します。

この test 中に cube button を押さないでください。button press は中断扱いになり、test は失敗します。

`test_id_information_2` には Standard ID Card が必要です。

手順:

1. cube を Standard ID Card `0` に touch します。
2. cube を Standard ID Card `E` に touch します。
3. 両方の card が検出されると test が終了します。

この test 中に cube button を押さないでください。button press は中断扱いになり、test は失敗します。

#### `test_notification_handler_v1_2.py`

`test_notification_1` は notification handler と handler context を確認します。

手順:

1. test を開始し、cube が接続されるまで待ちます。
2. cube の姿勢を変え、姿勢に応じて LED 色が変わることを確認します。
   - Top: blue。
   - Rear: green。
   - Left: red。
   - Front: cyan。
   - Right: magenta。
   - Bottom: yellow。
3. notification behavior を確認したら cube button を押します。

この test では、button press が正常な終了条件です。

#### `test_sensor_v1_2.py`

最初の4つの sensor test は手動操作が多く、時間がかかります。個別実行を推奨します。

`test_sensor_1` は Euler angle notification を確認します。

手順:

1. cube を自由に回転できる状態にします。
2. Top / Bottom posture では、yaw を `-180` から `165` 度まで約15度刻みで回転させます。
3. Front / Rear posture では、pitch が約 `90` 度 / `-90` 度になる状態を作ります。
4. Left / Right posture では、roll が約 `90` 度 / `-90` 度になる状態を作ります。
5. 各 target は約5度以内に合わせます。
6. yaw、pitch、roll がすべて0付近になると、cube は Enter sound effect を鳴らします。

cube button を押さないでください。button press は中断扱いになります。

`test_sensor_2` は high-precision Euler angle notification を確認します。
手順は `test_sensor_1` と同じです。

`test_sensor_3` は quaternion notification を確認します。

手順:

1. cube を x、y、z 各軸まわりに回転させます。
2. 各軸について、おおよそ `0`, `45`, `90`, `135`, `180`, `225`, `270`, `315` 度に
   対応する quaternion value を満たします。
3. 許容範囲は広めですが、各軸まわりの意図的な回転が必要です。
4. quaternion が identity orientation に近い場合、cube は Enter sound effect を鳴らします。

cube button を押さないでください。button press は中断扱いになります。

`test_sensor_4` は motion detection data の網羅確認です。

手順:

1. horizontal / non-horizontal の両方の状態を作ります。
2. collision なし / collision ありの両方の状態を作ります。
3. double tap なし / double tap ありの両方の状態を作ります。
4. cube を各面に置き、6種類すべての posture value を検出させます。
5. cube を強さを変えて振り、shake level `0` から `9` を検出させます。

この test は列挙されたすべての状態を観測する必要があるため、interactive test の中で
最も完了が難しい test です。cube button を押さないでください。button press は中断扱いになります。

`test_sensor_5`, `test_sensor_6`, `test_sensor_7` は read API の確認です。

- `test_sensor_5` は high-precision Euler data を10回読み取ります。
- `test_sensor_6` は quaternion data を10回読み取ります。
- `test_sensor_7` は motion detection data を10回読み取ります。

これらの test は通常、cube 接続後に特別な手動操作を必要としません。

### `tests/test_11_cube_off`

特定の cube だけが電源 ON の状態での cube discovery behavior を確認する hardware test
です。remote power off command で片方の cube の電源を落とすため、開始時には 2 台の
cube の電源を入れておく必要があります。

## Cube 設定ファイル

hardware test は、テストで使う cube を識別するために `tests/_cubes.py` を使います。
session setup は `tests/make_cube_list.py` を実行して、このファイルを生成できます。

典型的な流れ:

1. 必要な cube の電源を入れます。
2. 実行したい hardware test を開始します。
3. prompt が表示されたら Enter を押して `tests/_cubes.py` を生成します。
4. 既存の `tests/_cubes.py` を再利用する場合は、`s` を入力します。

## 注意

- hardware test の前に、実機 cube を十分に充電してください。
- scanner behavior を確認する場合は、無関係な BLE device が多い場所での実行を避けてください。
- code change を検証するときは、hardware test の前に definition-level test を実行してください。
