# Changelog

## [Unreleased]

### Added

- Support for toio BLE protocol version v2.4.0
- Compatibility with Python 3.8 and later versions
- Support for Pythonista3 application (#1)
- `py.typed` file for enhanced type hinting
- `AsyncSimpleCube` class to facilitate simple API usage with asyncio
- `MultipleToioCoreCubes` class for simplified control of multiple cubes
- `is_connect()` method in `CubeInterface` class to check connection status
- Initialization with `Sequence` in `cube.api.indicator` functions
- Initialization with `Sequence` in `cube.api.motor_control` functions
- `DummyInterface` class for debugging purposes
- `NotificationHandlerInfo` class as a second argument for notification handlers

### Changed

- `ToioCoreCube` class now verifies protocol version during connection

### Fixed

- Issue where `cube.api.sound.stop()` did not function (#3)
- Inability of `SimpleCube.play_sound()` to play sounds longer than 250ms
- Potential failures when using `concurrent.futures` or `threading.Thread`

## [1.0.2]

### Changed

- Updated document
- Changed minimum `bleak` version to 0.20.1

## [1.0.1]

- First Release
