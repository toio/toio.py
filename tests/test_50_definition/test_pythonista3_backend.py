#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     test_pythonista3_backend.py
#
#     Copyright 2026 Sony Interactive Entertainment Inc.
#
# ************************************************************

import asyncio
import gc
import importlib
import sys
import types
import weakref
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import (
    BleakBluetoothNotAvailableError,
    BleakBluetoothNotAvailableReason,
    BleakError,
    BleakGATTProtocolError,
)
from bleak.uuids import normalize_uuid_16

PERIPHERAL_UUID = "ABCDEF01-2345-6789-ABCD-EF0123456789"
SERVICE_UUID = "10B20100-5B3B-4571-9508-CF3EFCD7BBAE"
CHAR_UUID = "10B20101-5B3B-4571-9508-CF3EFCD7BBAE"
CCCD_UUID = "2902"
USER_DESCRIPTION_UUID = "2901"
OTHER_DESCRIPTOR_UUID = "2904"

PROPERTY_READ = 0x02
PROPERTY_WRITE_WITHOUT_RESPONSE = 0x04
PROPERTY_NOTIFY = 0x10
MAX_WRITE_SIZE = 20
ATT_HEADER_SIZE = 3
ATT_ERROR_READ_NOT_PERMITTED = 2
STATE_CONNECTED = 2
STATE_DISCONNECTED = 0
WRITE_WITH_RESPONSE = 0
WRITE_WITHOUT_RESPONSE = 1


class FakeNSNumber:
    """Mimics an NSNumber from objc_util, which only converts through str()."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def intValue(self):
        return self.value


class FakeUUID:
    def __init__(self, uuid):
        self.uuid = uuid

    def UUIDString(self):
        return self.uuid


class FakeError:
    def __init__(self, domain, code):
        self._domain = domain
        self._code = code

    def domain(self):
        return self._domain

    def code(self):
        return self._code


class FakeDescriptor:
    def __init__(self, uuid, handle, value):
        self._uuid = FakeUUID(uuid)
        self._handle = FakeNSNumber(handle)
        self._value = value

    def UUID(self):
        return self._uuid

    def handle(self):
        return self._handle

    def value(self):
        return self._value


class FakeCharacteristic:
    def __init__(self, uuid, handle, properties, descriptors, value=b""):
        self._uuid = FakeUUID(uuid)
        self._handle = FakeNSNumber(handle)
        self._properties = properties
        self._descriptors = descriptors
        self._value = value

    def UUID(self):
        return self._uuid

    def handle(self):
        return self._handle

    def properties(self):
        return self._properties

    def descriptors(self):
        return self._descriptors

    def value(self):
        return self._value


class FakeService:
    def __init__(self, uuid, handle, characteristics):
        self._uuid = FakeUUID(uuid)
        self._handle = FakeNSNumber(handle)
        self._characteristics = characteristics

    def UUID(self):
        return self._uuid

    def startHandle(self):
        return self._handle

    def characteristics(self):
        return self._characteristics


class FakePeripheral:
    """CBPeripheral which answers each request through the delegate methods."""

    def __init__(self, services, name="toio Core Cube-a1b"):
        self._services = services
        self._name = name
        self._identifier = FakeUUID(PERIPHERAL_UUID)
        self.manager = None
        self.delegate = None
        self.connection_state = STATE_DISCONNECTED
        self.written_value = None

    def _post(self, method, *args):
        asyncio.get_running_loop().call_soon(method, self, *args)

    def identifier(self):
        return self._identifier

    def name(self):
        return self._name

    def state(self):
        return self.connection_state

    def maximumWriteValueLengthForType_(self, _write_type):
        return MAX_WRITE_SIZE

    def discoverServices_(self, _services):
        self._post(self.manager.did_discover_services, self._services, None)

    def discoverCharacteristics_forService_(self, _uuids, service):
        self._post(
            self.manager.did_discover_characteristics_for_service,
            service,
            service.characteristics(),
            None,
        )

    def discoverDescriptorsForCharacteristic_(self, characteristic):
        self._post(
            self.manager.did_discover_descriptors_for_characteristic,
            characteristic,
            None,
        )

    def readValueForCharacteristic_(self, characteristic):
        self._post(
            self.manager.did_update_value_for_characteristic,
            characteristic,
            characteristic.value(),
            None,
        )

    def readValueForDescriptor_(self, descriptor):
        self._post(
            self.manager.did_update_value_for_descriptor,
            descriptor,
            descriptor.value(),
            None,
        )

    def writeValue_forCharacteristic_type_(self, value, characteristic, write_type):
        self.written_value = (value, write_type)
        self._post(
            self.manager.did_write_value_for_characteristic, characteristic, None
        )

    def setNotifyValue_forCharacteristic_(self, _enabled, characteristic):
        self._post(
            self.manager.did_update_notification_for_characteristic,
            characteristic,
            None,
        )


class FakeCentralManager:
    async def connect(self, peripheral, _disconnect_callback, timeout):
        peripheral.connection_state = STATE_CONNECTED

    async def disconnect(self, peripheral):
        peripheral.connection_state = STATE_DISCONNECTED


@pytest.fixture(scope="module")
def backend():
    """Imports the backend with a stubbed objc_util, which only exists on iOS."""
    objc_util = types.ModuleType("objc_util")
    objc_util.c = MagicMock(name="c")
    objc_util.ObjCClass = lambda name: MagicMock(name=name)
    objc_util.ObjCInstance = lambda obj: obj
    objc_util.nsdata_to_bytes = bytes
    objc_util.create_objc_class = MagicMock(name="create_objc_class")
    for name in ("NSArray", "NSDictionary", "NSNumber", "NSObject", "NSString"):
        setattr(objc_util, name, MagicMock(name=name))
    objc_util.NSData = MagicMock(name="NSData")

    def init_with_bytes(data, _length):
        # c_void_p, the type objc_util uses here, does not accept a bytearray.
        assert isinstance(data, bytes)
        return data

    objc_util.NSData.alloc.return_value.initWithBytes_length_.side_effect = (
        init_with_bytes
    )

    package = "toio.device_interface.pythonista3corebluetooth"
    with patch.dict(sys.modules, {"objc_util": objc_util}):
        yield types.SimpleNamespace(
            objc_util=objc_util,
            client=importlib.import_module(f"{package}.client"),
            scanner=importlib.import_module(f"{package}.scanner"),
            central=importlib.import_module(f"{package}.CentralManagerDelegate"),
            peripheral=importlib.import_module(f"{package}.PeripheralDelegate"),
        )


@pytest.fixture
def gatt():
    cccd = FakeDescriptor(CCCD_UUID, 13, FakeNSNumber(1))
    user_description = FakeDescriptor(USER_DESCRIPTION_UUID, 14, "motor")
    other = FakeDescriptor(OTHER_DESCRIPTOR_UUID, 15, b"\x01\x02\x03")
    characteristic = FakeCharacteristic(
        CHAR_UUID,
        12,
        PROPERTY_READ | PROPERTY_WRITE_WITHOUT_RESPONSE | PROPERTY_NOTIFY,
        [cccd, user_description, other],
        b"\x0a\x0b",
    )
    service = FakeService(SERVICE_UUID, 11, [characteristic])
    return types.SimpleNamespace(
        peripheral=FakePeripheral([service]),
        service=service,
        characteristic=characteristic,
        cccd=cccd,
        user_description=user_description,
        other=other,
    )


@pytest_asyncio.fixture
async def client(backend, gatt, mocker):
    real_manager = backend.peripheral.PeripheralManager

    def peripheral_manager(peripheral):
        peripheral.manager = real_manager(peripheral)
        return peripheral.manager

    mocker.patch.object(backend.client, "PeripheralManager", peripheral_manager)
    device = BLEDevice(PERIPHERAL_UUID, "toio", (gatt.peripheral, FakeCentralManager()))
    bleak_client = BleakClient(device, backend=backend.client.BleakClientPythonista3)
    await bleak_client.connect()
    return bleak_client


def advertisement(**overrides):
    data = {
        "kCBAdvDataServiceData": None,
        "kCBAdvDataManufacturerData": None,
        "kCBAdvDataServiceUUIDs": None,
        "kCBAdvDataTxPowerLevel": None,
        "kCBAdvDataLocalName": None,
    }
    data.update(overrides)
    return data


@pytest.fixture
def fake_scan_manager(backend, mocker):
    manager = MagicMock()
    manager.callbacks = {}
    manager.wait_until_ready = AsyncMock()
    manager.start_scan = AsyncMock()
    manager.stop_scan = AsyncMock()
    mocker.patch.object(backend.scanner, "CentralManager", lambda: manager)
    return manager


async def run_scan(backend, manager, adv, name="toio Core Cube", service_uuids=None):
    found = []
    scanner = BleakScanner(
        detection_callback=lambda device, data: found.append((device, data)),
        service_uuids=service_uuids,
        backend=backend.scanner.BleakScannerPythonista3,
    )
    async with scanner:
        callback = next(iter(manager.callbacks.values()))
        callback(FakePeripheral([], name=name), adv, -50)
    return found


@pytest.mark.asyncio
async def test_scan_reports_device_with_upper_case_address(backend, fake_scan_manager):
    adv = advertisement(
        kCBAdvDataLocalName="toio Core Cube",
        kCBAdvDataServiceUUIDs=[FakeUUID(SERVICE_UUID)],
    )

    found = await run_scan(backend, fake_scan_manager, adv)

    device, data = found[0]
    # The address filter in ble.py compares against an upper case address.
    assert device.address == PERIPHERAL_UUID
    assert device.name == "toio Core Cube"
    assert data.local_name == "toio Core Cube"
    assert data.service_uuids == [SERVICE_UUID.lower()]
    assert data.rssi == -50


@pytest.mark.asyncio
async def test_scan_keeps_missing_names_as_none(backend, fake_scan_manager):
    found = await run_scan(backend, fake_scan_manager, advertisement(), name=None)

    device, data = found[0]
    assert device.name is None
    assert data.local_name is None


@pytest.mark.asyncio
async def test_scan_drops_advertisement_outside_service_filter(
    backend, fake_scan_manager
):
    adv = advertisement(kCBAdvDataServiceUUIDs=[FakeUUID(SERVICE_UUID)])

    found = await run_scan(
        backend, fake_scan_manager, adv, service_uuids=[normalize_uuid_16(0x180F)]
    )

    assert found == []


@pytest.mark.asyncio
async def test_scan_propagates_unavailable_bluetooth(backend, fake_scan_manager):
    error = BleakBluetoothNotAvailableError(
        "off", BleakBluetoothNotAvailableReason.POWERED_OFF
    )
    fake_scan_manager.wait_until_ready.side_effect = error
    scanner = BleakScanner(backend=backend.scanner.BleakScannerPythonista3)

    with pytest.raises(BleakBluetoothNotAvailableError):
        await scanner.start()

    fake_scan_manager.start_scan.assert_not_called()


@pytest.mark.asyncio
async def test_connect_builds_gatt_tree_with_integer_handles(client):
    service = client.services.get_service(SERVICE_UUID)
    characteristic = client.services.get_characteristic(CHAR_UUID)

    assert service.handle == 11
    assert characteristic.handle == 12
    assert characteristic.service_handle == 11
    assert characteristic.service_uuid == SERVICE_UUID.lower()
    assert set(characteristic.properties) == {
        "read",
        "write-without-response",
        "notify",
    }
    assert characteristic.max_write_without_response_size == MAX_WRITE_SIZE
    assert [d.handle for d in characteristic.descriptors] == [13, 14, 15]
    assert characteristic.descriptors[0].characteristic_handle == 12


@pytest.mark.asyncio
async def test_connection_state_and_peripheral_information(client, gatt):
    assert client.is_connected is True
    assert client.name == "toio Core Cube-a1b"
    assert client.mtu_size == MAX_WRITE_SIZE + ATT_HEADER_SIZE

    await client.disconnect()

    assert client.is_connected is False


def test_client_accepts_address_string(backend):
    client = BleakClient(PERIPHERAL_UUID, backend=backend.client.BleakClientPythonista3)

    assert client.address == PERIPHERAL_UUID
    assert client.is_connected is False


def test_client_accepts_requested_services(backend):
    device = BLEDevice(PERIPHERAL_UUID, "toio", (MagicMock(), MagicMock()))

    client = BleakClient(
        device,
        services=[SERVICE_UUID],
        backend=backend.client.BleakClientPythonista3,
    )

    assert client.address == PERIPHERAL_UUID


@pytest.mark.asyncio
async def test_read_gatt_char_returns_bytearray(client):
    value = await client.read_gatt_char(CHAR_UUID)

    assert value == bytearray(b"\x0a\x0b")
    assert isinstance(value, bytearray)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response, write_type",
    [(True, WRITE_WITH_RESPONSE), (False, WRITE_WITHOUT_RESPONSE)],
)
async def test_write_gatt_char_selects_write_type(client, gatt, response, write_type):
    await client.write_gatt_char(CHAR_UUID, b"\x01\x02", response=response)

    assert gatt.peripheral.written_value == (b"\x01\x02", write_type)


@pytest.mark.asyncio
async def test_write_gatt_char_accepts_bytearray(client, gatt):
    await client.write_gatt_char(CHAR_UUID, bytearray(b"\x01"), response=False)

    assert gatt.peripheral.written_value == (b"\x01", WRITE_WITHOUT_RESPONSE)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handle, expected",
    [
        pytest.param(13, b"\x01\x00", id="nsnumber"),
        pytest.param(14, b"motor", id="nsstring"),
        pytest.param(15, b"\x01\x02\x03", id="nsdata"),
    ],
)
async def test_read_gatt_descriptor_returns_peripheral_bytes(client, handle, expected):
    value = await client.read_gatt_descriptor(handle)

    assert value == bytearray(expected)


@pytest.mark.asyncio
async def test_notification_reaches_callback_as_bytearray(client, gatt):
    received = []

    await client.start_notify(CHAR_UUID, lambda char, data: received.append(data))
    gatt.peripheral.manager.did_update_value_for_characteristic(
        gatt.peripheral, gatt.characteristic, b"\x03\x04", None
    )

    assert received == [bytearray(b"\x03\x04")]
    assert isinstance(received[0], bytearray)

    await client.stop_notify(CHAR_UUID)
    gatt.peripheral.manager.did_update_value_for_characteristic(
        gatt.peripheral, gatt.characteristic, b"\x05", None
    )

    assert len(received) == 1


@pytest.mark.asyncio
async def test_discriminator_separates_notification_from_pending_read(client, gatt):
    received = []
    manager = gatt.peripheral.manager
    await client.start_notify(
        CHAR_UUID,
        lambda char, data: received.append(data),
        cb={"notification_discriminator": lambda data: data[0] == 0xFF},
    )
    # The delegate answer is delivered manually to overlap it with a notification.
    gatt.peripheral.readValueForCharacteristic_ = lambda characteristic: None

    read = asyncio.create_task(client.read_gatt_char(CHAR_UUID))
    await asyncio.sleep(0)
    manager.did_update_value_for_characteristic(
        gatt.peripheral, gatt.characteristic, b"\xff\x01", None
    )
    manager.did_update_value_for_characteristic(
        gatt.peripheral, gatt.characteristic, b"\x01\x02", None
    )

    assert await read == bytearray(b"\x01\x02")
    assert received == [bytearray(b"\xff\x01")]


@pytest.mark.asyncio
async def test_att_error_raises_gatt_protocol_error(client, gatt):
    error = FakeError("CBATTErrorDomain", ATT_ERROR_READ_NOT_PERMITTED)
    manager = gatt.peripheral.manager
    gatt.peripheral.readValueForCharacteristic_ = lambda characteristic: (
        asyncio.get_running_loop().call_soon(
            manager.did_update_value_for_characteristic,
            gatt.peripheral,
            characteristic,
            None,
            error,
        )
    )

    with pytest.raises(BleakGATTProtocolError) as excinfo:
        await client.read_gatt_char(CHAR_UUID)

    assert excinfo.value.code == ATT_ERROR_READ_NOT_PERMITTED


@pytest.mark.asyncio
async def test_other_error_domain_raises_bleak_error(client, gatt):
    error = FakeError("CBErrorDomain", 7)
    manager = gatt.peripheral.manager
    gatt.peripheral.writeValue_forCharacteristic_type_ = lambda v, c, t: (
        asyncio.get_running_loop().call_soon(
            manager.did_write_value_for_characteristic, gatt.peripheral, c, error
        )
    )

    with pytest.raises(BleakError) as excinfo:
        await client.write_gatt_char(CHAR_UUID, b"\x01", response=True)

    assert not isinstance(excinfo.value, BleakGATTProtocolError)


@pytest.mark.asyncio
async def test_ble_cube_uses_backend_on_ios(backend, gatt, mocker):
    from toio.device_interface.ble import BleCube

    real_manager = backend.peripheral.PeripheralManager

    def peripheral_manager(peripheral):
        peripheral.manager = real_manager(peripheral)
        return peripheral.manager

    mocker.patch.object(backend.client, "PeripheralManager", peripheral_manager)
    mocker.patch("sys.platform", "ios")
    device = BLEDevice(PERIPHERAL_UUID, "toio", (gatt.peripheral, FakeCentralManager()))

    cube = BleCube(device)

    assert await cube.connect() is True
    assert await cube.read(CHAR_UUID) == bytearray(b"\x0a\x0b")
    assert await cube.disconnect() is True
    assert cube.is_connect() is False


def make_central_manager(backend, state, authorization=0):
    manager = backend.central.CentralManager()
    manager.central_manager.state.return_value = state
    manager.central_manager.authorization.return_value = authorization
    manager.did_update_state()
    return manager


@pytest.mark.asyncio
async def test_wait_until_ready_waits_for_state_update(backend):
    manager = backend.central.CentralManager()
    manager.central_manager.state.return_value = 5

    waiter = asyncio.create_task(manager.wait_until_ready())
    await asyncio.sleep(0)

    assert not waiter.done()

    manager.did_update_state()
    await waiter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, authorization, reason",
    [
        (2, 0, BleakBluetoothNotAvailableReason.NO_BLUETOOTH),
        (3, 2, BleakBluetoothNotAvailableReason.DENIED_BY_USER),
        (3, 1, BleakBluetoothNotAvailableReason.DENIED_BY_SYSTEM),
        (3, 0, BleakBluetoothNotAvailableReason.DENIED_BY_UNKNOWN),
        (4, 0, BleakBluetoothNotAvailableReason.POWERED_OFF),
        (1, 0, BleakBluetoothNotAvailableReason.UNKNOWN),
        (0, 0, BleakBluetoothNotAvailableReason.UNKNOWN),
    ],
)
async def test_wait_until_ready_reports_unavailable_reason(
    backend, state, authorization, reason
):
    manager = make_central_manager(backend, state, authorization)

    with pytest.raises(BleakBluetoothNotAvailableError) as excinfo:
        await manager.wait_until_ready()

    assert excinfo.value.reason == reason


@pytest.mark.asyncio
async def test_delegate_does_not_keep_central_manager_alive(backend):
    create_objc_class = backend.objc_util.create_objc_class
    manager = backend.central.CentralManager()
    methods = create_objc_class.call_args.kwargs["methods"]
    state_update = next(
        m for m in methods if m.__name__ == "centralManagerDidUpdateState_"
    )
    reference = weakref.ref(manager)

    del manager
    gc.collect()

    assert reference() is None
    # A callback arriving after the release must be ignored.
    state_update(None, None, MagicMock())


@pytest.mark.asyncio
async def test_rssi_is_converted_on_delegate_callback(backend, gatt):
    gatt.peripheral.readRSSI = lambda: None
    manager = backend.peripheral.PeripheralManager(gatt.peripheral)
    methods = backend.objc_util.create_objc_class.call_args.kwargs["methods"]
    did_read_rssi = next(
        m for m in methods if m.__name__ == "peripheral_didReadRSSI_error_"
    )

    read = asyncio.create_task(manager.read_rssi())
    await asyncio.sleep(0)
    did_read_rssi(None, None, gatt.peripheral, FakeNSNumber(-42), None)

    assert await read == -42
