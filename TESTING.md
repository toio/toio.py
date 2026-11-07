# Testing

This document explains how to run the test suite and what each test group
covers.

## Requirements

- Python 3.10 or later. Python 3.14 is recommended
- uv
- Development dependencies installed through uv
- Physical toio Core Cubes for hardware tests

Install or synchronize the development environment:

```bash
uv sync --dev
```

## Quick Test Run

Run definition-level tests that do not require physical cubes:

```bash
uv run pytest tests/test_50_definition
```

These tests use fakes and mocks. When only `tests/test_50_definition` is
selected, the test setup skips physical cube discovery.

## Full Test Run

Run the full pytest suite:

```bash
uv run pytest
```

The full suite includes tests that require physical toio Core Cubes. At session
startup, `tests/conftest.py` prompts for cube setup and may generate
`tests/_cubes.py` by scanning nearby cubes. Turn on the required cubes before
continuing. If `tests/_cubes.py` is already correct, type `s` and press Enter
to skip regeneration.

Many hardware tests include a 3-second wait between test cases. This is
intentional and helps avoid BLE state overlap between tests.

## Useful Commands

Run one test file:

```bash
uv run pytest tests/test_50_definition/test_scanner.py
```

Run one test:

```bash
uv run pytest tests/test_50_definition/test_scanner.py::test_base_ble_scanner_strategy_quick_returns_early
```

Show log output while running tests:

```bash
uv run pytest -s tests/test_50_definition
```

Run tests with coverage:

```bash
uv run coverage run --source=toio -m pytest tests/test_50_definition
uv run coverage report
```

## Test Groups

### `tests/test_50_definition`

Definition-level tests that do not require physical cubes.

Coverage includes:

- BLE connection state handling with mocked Bleak clients.
- Command byte generation and response parsing for the configuration and
  indicator commands.
- Scanner strategy behavior for `best` and `quick`, and the scanner keyword
  arguments accepted by the cube initializers.
- `ToioCoreCube` initialization from `CubeInfo`.
- Sensor payload dispatch for the posture angle notifications.
- Definition and import-level behavior that can be checked without BLE
  hardware.

These tests are the safest default for CI and local regression checks.

### `tests/test_50_single_cube`

Single-cube hardware tests.

Coverage includes:

- Connecting and disconnecting one cube.
- Battery, button, configuration, indicator, and sound APIs.
- Protocol-version-related connection behavior.
- Connection interval APIs.

These tests require at least one powered-on toio Core Cube.

### `tests/test_10_two_cubes`

Two-cube hardware tests.

Coverage includes:

- Scanner behavior with multiple cubes.
- Scan strategies `best` and `quick`, including their timing.
- Sorting by RSSI and local name.
- Scanning by cube ID and BLE address.
- Creating one or more `ToioCoreCube` instances from scanned cube data.
- Windows registered-cube scanning where supported.

These tests require two powered-on toio Core Cubes. On Windows, registered-cube
tests require the cubes to be paired with the OS.

### `tests/test_50_mat`

Motor and movement tests that require a toio mat.

Coverage includes:

- Motor control.
- Targeted movement.
- Multiple-target movement.
- Acceleration-based motor commands.

Place the cube on the required position ID mat before running these tests.

#### Running Mat Tests

Run all mat tests:

```bash
uv run pytest -s tests/test_50_mat
```

Run one file:

```bash
uv run pytest -s tests/test_50_mat/test_motor.py
uv run pytest -s tests/test_50_mat/test_motor_v1_2.py
```

Run one test:

```bash
uv run pytest -s tests/test_50_mat/test_motor.py::test_motor_2
```

Use `-s` so preparation prompts are visible. Keep only the target cube powered
on when possible, because these tests scan one nearby cube with
`BLEScanner.scan(1)`.

#### Mat Test Setup

1. Prepare one powered-on toio Core Cube.
2. Place the cube on a position ID mat where the coordinates used by the tests
   are readable.
3. Make sure the cube has enough free space to move around coordinates
   `(120, 210)`, `(250, 170)`, and `(350, 170)`.
4. Start the selected test.
5. If cube setup asks whether to generate `tests/_cubes.py`, press Enter to
   generate it or type `s` to reuse the existing file.
6. If the test uses the `confirm` fixture, position the cube safely on the mat
   and press Enter when ready.

`test_motor.py` and `test_motor_v1_2.py` exercise the same behavior. The former
uses typed API values such as `TargetPosition`, `Speed`, and enum values. The
latter uses tuple and integer forms for the same motor commands.

#### `test_motor_1`

This test does not require a target position, but it does move the cube.

Expected behavior:

1. The cube connects.
2. Both motors run with power `10` for about 2 seconds.
3. Both motors stop with `motor_control(0, 0)`.
4. The cube disconnects.

Keep the cube on a safe surface with enough room for a short straight movement.

#### `test_motor_2`

This test requires a position ID mat and uses the `confirm` fixture.

Expected behavior:

1. Place the cube on the position ID mat and press Enter at the prompt.
2. The cube connects and registers a motor notification handler.
3. The cube moves linearly to coordinate `(350, 170)` with angle `0`.
4. The command uses a maximum speed of `100` with acceleration and
   deceleration.
5. The test waits about 4 seconds, stops the motor, and disconnects.
6. The test passes only if a `ResponseMotorControlTarget` notification is
   received with `MotorResponseCode.SUCCESS`.

If the cube cannot read the mat, starts outside a valid area, is blocked, or
cannot reach the target within the command timeout, the response may not be
`SUCCESS`.

#### `test_motor_3`

This test requires a position ID mat.

Expected behavior:

1. Place the cube on the position ID mat.
2. The cube connects and registers a motor notification handler.
3. The cube moves linearly through two targets:
   - `(250, 170)` with angle `135`.
   - `(120, 210)` with angle `0`.
4. The command uses overwrite mode and a maximum speed of `100` with
   acceleration and deceleration.
5. The test waits about 5 seconds and disconnects.
6. The test passes only if a `ResponseMotorControlMultipleTargets`
   notification is received with `MotorResponseCode.SUCCESS`.

Make sure the path between the start point and both targets is clear.

#### `test_motor_4`

This test requires a safe surface or mat area with room for forward movement.

Expected behavior:

1. The cube connects.
2. The cube runs `motor_control_acceleration()` with translation `100`,
   acceleration `5`, no rotation velocity, forward direction, and
   translational-velocity priority.
3. The command duration is 2000 ms.
4. The test waits about 4 seconds and disconnects.

The test does not assert a motor response notification. Confirm that the cube
moves forward and then stops.

### `tests/test_20_interactive`

Interactive hardware tests that require manual observation or operation.

Coverage includes:

- Indicator behavior.
- ID information notifications.
- Notification handler behavior.
- Sensor and motion detection behavior.

Some tests ask the operator to confirm whether the observed cube behavior was
correct.

#### Running Interactive Tests

Run all interactive tests:

```bash
uv run pytest -s tests/test_20_interactive
```

Running the whole directory can take a long time because some sensor tests
require many manual cube orientations. For normal manual verification, run one
file or one test at a time:

```bash
uv run pytest -s tests/test_20_interactive/test_indicator.py
uv run pytest -s tests/test_20_interactive/test_id_information.py::test_id_information_1
uv run pytest -s tests/test_20_interactive/test_sensor_v1_2.py::test_sensor_5
```

Use `-s` so prompts and operator instructions are visible. Keep only the target
cube powered on when possible, because these tests scan one nearby cube with
`BLEScanner.scan(1)`.

#### Common Operator Flow

1. Power on the target cube.
2. Start the selected test with `uv run pytest -s ...`.
3. If cube setup asks whether to generate `tests/_cubes.py`, press Enter to
   generate it or type `s` to reuse the existing file.
4. If the test uses the `confirm` fixture, prepare the cube or mat and press
   Enter when prompted.
5. Follow the manual operation described for the test.
6. If the test uses the `get_result` fixture, press Enter for success or type
   `N` and press Enter for failure.

Some tests treat the cube button as an abort condition. Do not press the cube
button unless the procedure explicitly says to press it.

#### `test_indicator.py`

These tests require visual confirmation of the cube LED. Each test uses
`get_result`, so report the observed result at the final prompt.

- `test_indicator_turn_on`
  - Expected behavior: the LED turns purple (`#FF0080`) for about 2 seconds,
    then turns off.
- `test_indicator_turn_off_all`
  - Expected behavior: the LED turns light green (`#00FF40`), stays on for
    about 3 seconds, then turns off through `turn_off_all()`.
- `test_indicator_turn_off`
  - Expected behavior: the LED turns light green, stays on for about 3 seconds,
    then turns off through `turn_off(1)`.
- `test_indicator_repeated_turn_on`
  - Expected behavior: the LED alternates light green and purple at 500 ms
    intervals for 5 repeats, then turns off.

#### `test_id_information.py`

`test_id_information_1` requires a position ID mat.

Procedure:

1. Put the cube on the position ID mat.
2. Move the cube through all of these target areas and orientations:
   - `x=98..141`, `y=142..185`, angle about `0` degrees.
   - `x=356..399`, `y=142..185`, angle about `90` degrees.
   - `x=356..399`, `y=314..357`, angle about `180` degrees.
   - `x=98..141`, `y=314..357`, angle about `270` degrees.
3. Keep each orientation within about 5 degrees.
4. The test finishes when all target areas are detected.

Do not press the cube button during this test. Button press is treated as an
abort condition and the test fails.

`test_id_information_2` requires Standard ID Cards.

Procedure:

1. Touch the cube to Standard ID Card `0`.
2. Touch the cube to Standard ID Card `E`.
3. The test finishes when both cards are detected.

Do not press the cube button during this test. Button press is treated as an
abort condition and the test fails.

#### `test_notification_handler_v1_2.py`

`test_notification_1` checks notification handlers and handler context.

Procedure:

1. Start the test and wait for the cube to connect.
2. Change the cube posture and confirm that the LED changes color according to
   the posture:
   - Top: blue.
   - Rear: green.
   - Left: red.
   - Front: cyan.
   - Right: magenta.
   - Bottom: yellow.
3. Press the cube button after confirming notification behavior.

In this test, button press is the normal completion condition.

#### `test_sensor_v1_2.py`

The first four sensor tests are manual and can take a long time. Run them
individually.

`test_sensor_1` checks Euler angle notifications.

Procedure:

1. Prepare the cube so it can be freely rotated.
2. For Top and Bottom posture, rotate yaw through `-180` to `165` degrees in
   roughly 15-degree steps.
3. For Front and Rear posture, satisfy pitch angles around `90` and `-90`
   degrees.
4. For Left and Right posture, satisfy roll angles around `90` and `-90`
   degrees.
5. Keep each target within about 5 degrees.
6. The cube plays the Enter sound effect when yaw, pitch, and roll are near
   zero.

Do not press the cube button. Button press is treated as an abort condition.

`test_sensor_2` checks high-precision Euler angle notifications. Use the same
procedure as `test_sensor_1`.

`test_sensor_3` checks quaternion notifications.

Procedure:

1. Rotate the cube around the x, y, and z axes.
2. For each axis, satisfy the quaternion values corresponding roughly to
   `0`, `45`, `90`, `135`, `180`, `225`, `270`, and `315` degrees.
3. The tolerance is broad, but the test still requires deliberate rotations
   around each axis.
4. The cube plays the Enter sound effect when the quaternion is near the
   identity orientation.

Do not press the cube button. Button press is treated as an abort condition.

`test_sensor_4` checks motion detection data coverage.

Procedure:

1. Produce both horizontal states: horizontal and non-horizontal.
2. Produce both collision states: no collision and collision.
3. Produce both double-tap states: no double tap and double tap.
4. Produce all six posture values by placing the cube on each face.
5. Produce shake levels from `0` through `9` by shaking the cube with different
   strengths.

This test is the hardest interactive test to complete because every listed
state must be observed. Do not press the cube button. Button press is treated
as an abort condition.

`test_sensor_5`, `test_sensor_6`, and `test_sensor_7` are read API checks.

- `test_sensor_5` reads high-precision Euler data 10 times.
- `test_sensor_6` reads quaternion data 10 times.
- `test_sensor_7` reads motion detection data 10 times.

These tests normally do not require special manual movement after the cube is
connected.

### `tests/test_11_cube_off`

Hardware tests for cube discovery behavior when only selected cubes are powered
on. The test powers one cube down through the remote power off command, so two
powered-on cubes are needed at the start of the run.

## Cube Configuration File

Hardware tests use `tests/_cubes.py` to identify the cubes used by the test
suite. The session setup can generate this file by running
`tests/make_cube_list.py`.

Typical flow:

1. Turn on the required cubes.
2. Run the desired hardware tests.
3. Press Enter when prompted to generate `tests/_cubes.py`.
4. Type `s` instead if the existing `tests/_cubes.py` should be reused.

## Notes

- Keep physical cubes charged before running hardware tests.
- Avoid running hardware tests in an area with many unrelated BLE devices when
  scanner behavior is being checked.
- Run definition-level tests before hardware tests when validating code changes.
