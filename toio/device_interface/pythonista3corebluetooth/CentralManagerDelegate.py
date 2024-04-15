"""
CentralManagerDelegate will implement the CBCentralManagerDelegate protocol to
manage CoreBluetooth services and resources on the Central End

Created on June, 25 2019 by kevincar <kevincarrolldavis@gmail.com>

Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

import asyncio
import ctypes
import logging
import sys
import threading
from uuid import UUID

from typing_extensions import Any, Callable, Dict, Optional, TypeAlias

from toio.device_interface.pythonista3corebluetooth.utils import cb_uuid_to_uuid

if sys.version_info < (3, 11):
    from async_timeout import timeout as async_timeout
else:
    from asyncio import timeout as async_timeout

from bleak.exc import BleakError
from objc_util import (
    NSArray,
    NSDictionary,
    NSNumber,
    NSString,
    ObjCInstance,
    c,
    create_objc_class,
)

from .objc_types import (
    CBUUID,
    DISPATCH_QUEUE_SERIAL,
    CBCentralManager,
    CBCentralManagerType,
    CBManagerStatePoweredOff,
    CBManagerStatePoweredOn,
    CBManagerStateResetting,
    CBManagerStateUnauthorized,
    CBManagerStateUnknown,
    CBManagerStateUnsupported,
    CBPeripheral,
    CBPeripheralType,
    CBService,
    CBServiceType,
    CBUUIDType,
    NSError,
    NSErrorType,
    NSKeyValueChangeNewKey,
    NSKeyValueObservingOptionNew,
    dispatch_queue_create,
)

logger = logging.getLogger(__name__)

DisconnectCallback = Callable[[], None]


class CentralManager:
    """iOS conforming python class for managing the CentralManger for BLE"""

    def __init__(self):
        self.event_loop = asyncio.get_running_loop()
        self._connect_futures: Dict[UUID, asyncio.Future] = {}

        self.callbacks: Dict[
            int, Callable[[CBPeripheralType, Dict[str, Any], int], None]
        ] = {}
        self._disconnect_callbacks: Dict[UUID, DisconnectCallback] = {}
        self._disconnect_futures: Dict[UUID, asyncio.Future] = {}

        self._did_update_state_event = threading.Event()
        self.delegate = self.create_delegate()
        self.central_manager = CBCentralManager.alloc().initWithDelegate_queue_(
            self.delegate,
            dispatch_queue_create(
                "bleak.pythonista3corebluetooth", DISPATCH_QUEUE_SERIAL
            ),
        )

        # according to CoreBluetooth docs, it is not valid to call CBCentral
        # methods until the centralManagerDidUpdateState_() delegate method
        # is called and the current state is CBManagerStatePoweredOn.
        # It doesn't take long for the callback to occur, so we should be able
        # to do a blocking wait here without anyone complaining.
        self._did_update_state_event.wait(1)

        if self.central_manager.state() == CBManagerStateUnsupported:
            raise BleakError("BLE is unsupported")

        if self.central_manager.state() == CBManagerStateUnauthorized:
            raise BleakError("BLE is not authorized - check macOS privacy settings")

        if self.central_manager.state() != CBManagerStatePoweredOn:
            raise BleakError("Bluetooth device is turned off")

        self.central_manager.addObserver_forKeyPath_options_context_(
            self, "isScanning", NSKeyValueObservingOptionNew, 0
        )
        self._did_start_scanning_event: Optional[asyncio.Event] = None
        self._did_stop_scanning_event: Optional[asyncio.Event] = None

    def __del__(self):
        try:
            self.central_manager.removeObserver_forKeyPath_(self, "isScanning")
        except IndexError:
            # If self.init() raised an exception before calling
            # addObserver_forKeyPath_options_context_, attempting
            # to remove the observer will fail with IndexError
            pass

    # User defined functions

    async def start_scan(self, service_uuids) -> None:
        service_uuids = (
            NSArray.alloc().initWithArray_(
                list(map(CBUUID.UUIDWithString_, service_uuids))
            )
            if service_uuids
            else None
        )

        self.central_manager.scanForPeripheralsWithServices_options_(
            service_uuids, None
        )

        event = asyncio.Event()
        self._did_start_scanning_event = event
        if not self.central_manager.isScanning():
            await event.wait()

    async def stop_scan(self) -> None:
        self.central_manager.stopScan()
        event = asyncio.Event()
        self._did_stop_scanning_event = event
        if self.central_manager.isScanning():
            await event.wait()

    async def connect(
        self,
        peripheral: CBPeripheralType,
        disconnect_callback: DisconnectCallback,
        timeout=10.0,
    ) -> None:
        peripheral_uuid = cb_uuid_to_uuid(peripheral.identifier())
        try:
            self._disconnect_callbacks[peripheral_uuid] = disconnect_callback
            future = self.event_loop.create_future()

            self._connect_futures[peripheral_uuid] = future
            try:
                self.central_manager.connectPeripheral_options_(peripheral, None)
                async with async_timeout(timeout):
                    await future
            finally:
                del self._connect_futures[peripheral_uuid]

        except asyncio.TimeoutError:
            logger.debug(f"Connection timed out after {timeout} seconds.")
            del self._disconnect_callbacks[peripheral_uuid]
            future = self.event_loop.create_future()

            self._disconnect_futures[peripheral_uuid] = future
            try:
                self.central_manager.cancelPeripheralConnection_(peripheral)
                await future
            finally:
                del self._disconnect_futures[peripheral_uuid]

            raise

    async def disconnect(self, peripheral: CBPeripheralType) -> None:
        future = self.event_loop.create_future()
        peripheral_uuid = cb_uuid_to_uuid(peripheral.identifier())

        self._disconnect_futures[peripheral_uuid] = future
        try:
            self.central_manager.cancelPeripheralConnection_(peripheral)
            await future
        finally:
            del self._disconnect_futures[peripheral_uuid]

    def _changed_is_scanning(self, is_scanning: bool) -> None:
        if is_scanning:
            if self._did_start_scanning_event:
                self._did_start_scanning_event.set()
        else:
            if self._did_stop_scanning_event:
                self._did_stop_scanning_event.set()

    def observeValueForKeyPath_ofObject_change_context_(
        self, keyPath: NSString, object: Any, change: NSDictionary, context: int
    ) -> None:
        logger.debug("'%s' changed", keyPath)

        if keyPath != "isScanning":
            return

        is_scanning = bool(change[NSKeyValueChangeNewKey])
        self.event_loop.call_soon_threadsafe(self._changed_is_scanning, is_scanning)

    def did_discover_peripheral(
        self,
        central: CBCentralManagerType,
        peripheral: CBPeripheralType,
        advertisementData: NSDictionary,
        RSSI: NSNumber,
    ) -> None:
        # Note: this function might be called several times for same device.
        # This can happen for instance when an active scan is done, and the
        # second call with contain the data from the BLE scan response.
        # Example a first time with the following keys in advertisementData:
        # ['kCBAdvDataLocalName', 'kCBAdvDataIsConnectable', 'kCBAdvDataChannel']
        # ... and later a second time with other keys (and values) such as:
        # ['kCBAdvDataServiceUUIDs', 'kCBAdvDataIsConnectable', 'kCBAdvDataChannel']
        #
        # i.e it is best not to trust advertisementData for later use and data
        # from it should be copied.
        #
        # This behaviour could be affected by the
        # CBCentralManagerScanOptionAllowDuplicatesKey global setting.

        uuid_string = peripheral.identifier().UUIDString()

        logger.debug(
            "Discovered device %s: %s @ RSSI: %d (kCBAdvData %r) and Central: %r",
            uuid_string,
            peripheral,
            RSSI,
            advertisementData,
            central,
        )

        for callback in self.callbacks.values():
            if callable(callback):
                callback(peripheral, advertisementData, RSSI)

    def did_connect_peripheral(
        self, central: CBCentralManagerType, peripheral: CBPeripheralType
    ) -> None:
        peripheral_uuid = cb_uuid_to_uuid(peripheral.identifier())
        future = self._connect_futures.get(peripheral_uuid, None)
        if future is not None:
            future.set_result(True)

    def did_fail_to_connect_peripheral(
        self,
        centralManager: CBCentralManagerType,
        peripheral: CBPeripheralType,
        error: Optional[NSErrorType],
    ) -> None:
        peripheral_uuid = cb_uuid_to_uuid(peripheral.identifier())
        future = self._connect_futures.get(peripheral_uuid, None)
        if future is not None:
            if error is not None:
                future.set_exception(BleakError(f"failed to connect: {error}"))
            else:
                future.set_result(False)

    def did_disconnect_peripheral(
        self,
        central: CBCentralManagerType,
        peripheral: CBPeripheralType,
        error: Optional[NSErrorType],
    ) -> None:
        logger.debug("Peripheral Device disconnected!")

        peripheral_uuid = cb_uuid_to_uuid(peripheral.identifier())
        future = self._disconnect_futures.get(peripheral_uuid, None)
        if future is not None:
            if error is not None:
                future.set_exception(BleakError(f"disconnect failed: {error}"))
            else:
                future.set_result(None)

        callback = self._disconnect_callbacks.pop(peripheral_uuid, None)

        if callback is not None:
            callback()

    def create_delegate(self):
        # Protocol Functions

        def centralManagerDidUpdateState_(_self, _cmd, ct_id):
            central = ObjCInstance(ct_id)
            logger.debug("centralManagerDidUpdateState_")
            if central.state() == CBManagerStateUnknown:
                logger.debug("Cannot detect bluetooth device")
            elif central.state() == CBManagerStateResetting:
                logger.debug("Bluetooth is resetting")
            elif central.state() == CBManagerStateUnsupported:
                logger.debug("Bluetooth is unsupported")
            elif central.state() == CBManagerStateUnauthorized:
                logger.debug("Bluetooth is unauthorized")
            elif central.state() == CBManagerStatePoweredOff:
                logger.debug("Bluetooth powered off")
            elif central.state() == CBManagerStatePoweredOn:
                logger.debug("Bluetooth powered on")

            self._did_update_state_event.set()

        def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
            _self, _cmd, ct_id, pe_id, adv_id, rssi_id
        ):
            logger.debug("centralManager_didDiscoverPeripheral_advertisementData_RSSI_")
            central = ObjCInstance(ct_id)
            peripheral = ObjCInstance(pe_id)
            advertisement_data = ObjCInstance(adv_id)
            rssi = ObjCInstance(rssi_id)
            self.event_loop.call_soon_threadsafe(
                self.did_discover_peripheral,
                central,
                peripheral,
                advertisement_data,
                rssi.intValue(),
            )

        def centralManager_didConnectPeripheral_(_self, _cmd, ct_id, pe_id):
            logger.debug("centralManager_didConnectPeripheral_")
            central = ObjCInstance(ct_id)
            peripheral = ObjCInstance(pe_id)
            self.event_loop.call_soon_threadsafe(
                self.did_connect_peripheral, central, peripheral
            )

        def centralManager_didFailToConnectPeripheral_error_(
            _self, _cmd, ctmg_id, pe_id, err_id
        ):
            logger.debug("centralManager_didFailToConnectPeripheral_error_")
            central_manager = ObjCInstance(ctmg_id)
            peripheral = ObjCInstance(pe_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self.event_loop.call_soon_threadsafe(
                self.did_fail_to_connect_peripheral, central_manager, peripheral, error
            )

        def centralManager_didDisconnectPeripheral_error_(
            _self, _cmd, ct_id, pe_id, err_id
        ):
            logger.debug("centralManager_didDisconnectPeripheral_error_")
            central = ObjCInstance(ct_id)
            peripheral = ObjCInstance(pe_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self.event_loop.call_soon_threadsafe(
                self.did_disconnect_peripheral, central, peripheral, error
            )

        methods = [
            centralManagerDidUpdateState_,
            centralManager_didDiscoverPeripheral_advertisementData_RSSI_,
            centralManager_didConnectPeripheral_,
            centralManager_didFailToConnectPeripheral_error_,
            centralManager_didDisconnectPeripheral_error_,
        ]

        central_delegate_class = create_objc_class(
            "central_delegate_class",
            methods=methods,
            protocols="CBCentralManagerDelegate",
        )
        delegate_instance = central_delegate_class.alloc().init()

        return delegate_instance
