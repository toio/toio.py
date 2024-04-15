"""

PeripheralDelegate

Created by kevincar <kevincarrolldavis@gmail.com>

Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

import asyncio
import itertools
import logging
import math
import sys
from enum import IntEnum
from uuid import UUID

from typing_extensions import Any, Dict, Iterable, NewType, Optional, TypeAlias

if sys.version_info < (3, 11):
    from async_timeout import timeout as async_timeout
else:
    from asyncio import timeout as async_timeout

from bleak.backends.client import NotifyCallback
from bleak.exc import BleakError
from objc_util import (
    NSArray,
    NSData,
    NSNumber,
    NSObject,
    NSString,
    ObjCInstance,
    create_objc_class,
    nsdata_to_bytes,
)

from .objc_types import (
    CBUUID,
    DISPATCH_QUEUE_SERIAL,
    CBCentralManager,
    CBCentralManagerType,
    CBCharacteristic,
    CBCharacteristicType,
    CBDescriptor,
    CBDescriptorType,
    CBManagerStatePoweredOff,
    CBManagerStatePoweredOn,
    CBManagerStateResetting,
    CBManagerStateUnauthorized,
    CBManagerStateUnknown,
    CBManagerStateUnsupported,
    CBPeripheral,
    CBPeripheralManager,
    CBPeripheralManagerType,
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

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CBCharacteristicWriteType(IntEnum):
    CBCharacteristicWriteWithResponse = 0
    CBCharacteristicWriteWithoutResponse = 1


class PeripheralManager:
    """iOS conforming python class for managing the PeripheralDelegate for BLE"""

    def __init__(self, peripheral: CBPeripheralType):
        """iOS init function for NSObject"""

        self.peripheral = peripheral
        self.peripheral.delegate = self.create_delegate()

        self._event_loop = asyncio.get_running_loop()
        self._services_discovered_future = self._event_loop.create_future()

        self._service_characteristic_discovered_futures: Dict[int, asyncio.Future] = {}
        self._characteristic_descriptor_discover_futures: Dict[int, asyncio.Future] = {}

        self._characteristic_read_futures: Dict[int, asyncio.Future] = {}
        self._characteristic_write_futures: Dict[int, asyncio.Future] = {}

        self._descriptor_read_futures: Dict[int, asyncio.Future] = {}
        self._descriptor_write_futures: Dict[int, asyncio.Future] = {}

        self._characteristic_notify_change_futures: Dict[int, asyncio.Future] = {}
        self._characteristic_notify_callbacks: Dict[int, NotifyCallback] = {}

        self._read_rssi_futures: Dict[UUID, asyncio.Future] = {}

    def futures(self) -> Iterable[asyncio.Future]:
        """
        Gets all futures for this delegate.

        These can be used to handle any pending futures when a peripheral is disconnected.
        """
        services_discovered_future = (
            (self._services_discovered_future,)
            if hasattr(self, "_services_discovered_future")
            else ()
        )

        return itertools.chain(
            services_discovered_future,
            self._service_characteristic_discovered_futures.values(),
            self._characteristic_descriptor_discover_futures.values(),
            self._characteristic_read_futures.values(),
            self._characteristic_write_futures.values(),
            self._descriptor_read_futures.values(),
            self._descriptor_write_futures.values(),
            self._characteristic_notify_change_futures.values(),
            self._read_rssi_futures.values(),
        )

    async def discover_services(self, services):
        logger.info("discover_services")
        future = self._event_loop.create_future()

        self._services_discovered_future = future
        try:
            logger.info(self.peripheral)
            # self.peripheral.discoverServices_(services)
            self.peripheral.discoverServices_(None)
            logger.info("return future")
            return await future
        finally:
            del self._services_discovered_future

    async def discover_characteristics(self, service: CBServiceType):
        future = self._event_loop.create_future()

        self._service_characteristic_discovered_futures[service.startHandle()] = future
        try:
            self.peripheral.discoverCharacteristics_forService_(None, service)
            return await future
        finally:
            del self._service_characteristic_discovered_futures[service.startHandle()]

    async def discover_descriptors(
        self, characteristic: CBCharacteristicType
    ) -> NSArray:
        future = self._event_loop.create_future()

        self._characteristic_descriptor_discover_futures[characteristic.handle()] = (
            future
        )
        try:
            self.peripheral.discoverDescriptorsForCharacteristic_(characteristic)
            await future
        finally:
            del self._characteristic_descriptor_discover_futures[
                characteristic.handle()
            ]

        return characteristic.descriptors()

    async def read_characteristic(
        self,
        characteristic: CBCharacteristicType,
        use_cached: bool = True,
        timeout: int = 20,
    ) -> NSData:
        if characteristic.value() is not None and use_cached:
            return characteristic.value()

        future = self._event_loop.create_future()

        self._characteristic_read_futures[characteristic.handle()] = future
        try:
            self.peripheral.readValueForCharacteristic_(characteristic)
            async with async_timeout(timeout):
                return await future
        finally:
            del self._characteristic_read_futures[characteristic.handle()]

    async def read_descriptor(
        self, descriptor: CBDescriptorType, use_cached: bool = True
    ) -> Any:
        if descriptor.value() is not None and use_cached:
            return descriptor.value()

        future = self._event_loop.create_future()

        self._descriptor_read_futures[descriptor.handle()] = future
        try:
            self.peripheral.readValueForDescriptor_(descriptor)
            return await future
        finally:
            del self._descriptor_read_futures[descriptor.handle()]

    async def write_characteristic(
        self,
        characteristic: CBCharacteristicType,
        value: NSData,
        response: CBCharacteristicWriteType,
    ) -> None:
        # in CoreBluetooth there is no indication of success or failure of
        # CBCharacteristicWriteWithoutResponse
        if response == CBCharacteristicWriteType.CBCharacteristicWriteWithResponse:
            future = self._event_loop.create_future()

            self._characteristic_write_futures[characteristic.handle()] = future
            try:
                self.peripheral.writeValue_forCharacteristic_type_(
                    value, characteristic, response
                )
                await future
            finally:
                del self._characteristic_write_futures[characteristic.handle()]
        else:
            self.peripheral.writeValue_forCharacteristic_type_(
                value, characteristic, response
            )

    async def write_descriptor(
        self, descriptor: CBDescriptorType, value: NSData
    ) -> None:
        future = self._event_loop.create_future()

        self._descriptor_write_futures[descriptor.handle()] = future
        try:
            self.peripheral.writeValue_forDescriptor_(value, descriptor)
            await future
        finally:
            del self._descriptor_write_futures[descriptor.handle()]

    async def start_notifications(
        self, characteristic: CBCharacteristicType, callback: NotifyCallback
    ) -> None:
        c_handle = characteristic.handle()
        if c_handle in self._characteristic_notify_callbacks:
            raise ValueError("Characteristic notifications already started")

        self._characteristic_notify_callbacks[c_handle] = callback

        future = self._event_loop.create_future()

        self._characteristic_notify_change_futures[c_handle] = future
        try:
            self.peripheral.setNotifyValue_forCharacteristic_(True, characteristic)
            await future
        finally:
            del self._characteristic_notify_change_futures[c_handle]

    async def stop_notifications(self, characteristic: CBCharacteristicType) -> None:
        c_handle = characteristic.handle()
        if c_handle not in self._characteristic_notify_callbacks:
            raise ValueError("Characteristic notification never started")

        future = self._event_loop.create_future()

        self._characteristic_notify_change_futures[c_handle] = future
        try:
            self.peripheral.setNotifyValue_forCharacteristic_(False, characteristic)
            await future
        finally:
            del self._characteristic_notify_change_futures[c_handle]

        self._characteristic_notify_callbacks.pop(c_handle)

    async def read_rssi(self) -> NSNumber:
        future = self._event_loop.create_future()

        self._read_rssi_futures[self.peripheral.identifier()] = future
        try:
            self.peripheral.readRSSI()
            return await future
        finally:
            del self._read_rssi_futures[self.peripheral.identifier()]

    def did_discover_services(
        self,
        peripheral: CBPeripheralType,
        services: NSArray,
        error: Optional[NSErrorType],
    ) -> None:
        future = self._services_discovered_future
        if error is not None:
            exception = BleakError(f"Failed to discover services {error}")
            future.set_exception(exception)
        else:
            logger.debug("Services discovered")
            future.set_result(services)

    def did_discover_characteristics_for_service(
        self,
        peripheral: CBPeripheralType,
        service: CBServiceType,
        characteristics: NSArray,
        error: Optional[NSErrorType],
    ):
        future = self._service_characteristic_discovered_futures.get(
            service.startHandle()
        )
        if not future:
            logger.debug(
                f"Unexpected event didDiscoverCharacteristicsForService for {service.startHandle()}"
            )
            return
        if error is not None:
            exception = BleakError(
                f"Failed to discover characteristics for service {service.startHandle()}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug("Characteristics discovered")
            future.set_result(characteristics)

    def did_discover_descriptors_for_characteristic(
        self,
        peripheral: CBPeripheralType,
        characteristic: CBCharacteristicType,
        error: Optional[NSErrorType],
    ):
        future = self._characteristic_descriptor_discover_futures.get(
            characteristic.handle()
        )
        if not future:
            logger.warning(
                f"Unexpected event didDiscoverDescriptorsForCharacteristic for {characteristic.handle()}"
            )
            return
        if error is not None:
            exception = BleakError(
                f"Failed to discover descriptors for characteristic {characteristic.handle()}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug(f"Descriptor discovered {characteristic.handle()}")
            future.set_result(None)

    def did_update_value_for_characteristic(
        self,
        peripheral: CBPeripheralType,
        characteristic: CBCharacteristicType,
        value: NSData,
        error: Optional[NSErrorType],
    ):
        c_handle = characteristic.handle()

        future = self._characteristic_read_futures.get(c_handle)

        # If there is no pending read request, then this must be a notification
        # (the same delegate callback is used by both).
        if not future:
            if error is None:
                notify_callback = self._characteristic_notify_callbacks.get(c_handle)

                if notify_callback:
                    notify_callback(nsdata_to_bytes(value))
            return

        if error is not None:
            exception = BleakError(f"Failed to read characteristic {c_handle}: {error}")
            future.set_exception(exception)
        else:
            logger.debug("Read characteristic value")
            future.set_result(value)

    def did_update_value_for_descriptor(
        self,
        peripheral: CBPeripheralType,
        descriptor: CBDescriptorType,
        value: NSObject,
        error: Optional[NSErrorType],
    ):
        future = self._descriptor_read_futures.get(descriptor.handle())
        if not future:
            logger.warning("Unexpected event didUpdateValueForDescriptor")
            return
        if error is not None:
            exception = BleakError(
                f"Failed to read descriptor {descriptor.handle()}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug("Read descriptor value")
            str_value = str(value)
            try:
                int_value = int(str(value))
                length = (
                    1
                    if int_value == 0
                    else math.ceil(math.log(int_value) / math.log(256))
                )
                result = int_value.to_bytes(length, "little")
            except:
                result = str_value.encode("utf-8")

            future.set_result(result)

    def did_write_value_for_characteristic(
        self,
        peripheral: CBPeripheralType,
        characteristic: CBCharacteristicType,
        error: Optional[NSErrorType],
    ):
        future = self._characteristic_write_futures.get(characteristic.handle(), None)
        if not future:
            return  # event only expected on write with response
        if error is not None:
            exception = BleakError(
                f"Failed to write characteristic {characteristic.handle()}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug("Write Characteristic Value")
            future.set_result(None)

    def did_write_value_for_descriptor(
        self,
        peripheral: CBPeripheralType,
        descriptor: CBDescriptorType,
        error: Optional[NSErrorType],
    ):
        future = self._descriptor_write_futures.get(descriptor.handle())
        if not future:
            logger.warning("Unexpected event didWriteValueForDescriptor")
            return
        if error is not None:
            exception = BleakError(
                f"Failed to write descriptor {descriptor.handle()}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug("Write Descriptor Value")
            future.set_result(None)

    def did_update_notification_for_characteristic(
        self,
        peripheral: CBPeripheralType,
        characteristic: CBCharacteristicType,
        error: Optional[NSErrorType],
    ):
        c_handle = characteristic.handle()
        future = self._characteristic_notify_change_futures.get(c_handle)
        if not future:
            logger.warning(
                "Unexpected event didUpdateNotificationStateForCharacteristic"
            )
            return
        if error is not None:
            exception = BleakError(
                f"Failed to update the notification status for characteristic {c_handle}: {error}"
            )
            future.set_exception(exception)
        else:
            logger.debug("Character Notify Update")
            future.set_result(None)

    def did_read_rssi(
        self, peripheral: CBPeripheralType, rssi: NSNumber, error: Optional[NSErrorType]
    ) -> None:
        future = self._read_rssi_futures.get(peripheral.identifier(), None)

        if not future:
            logger.warning("Unexpected event did_read_rssi")
            return

        if error is not None:
            exception = BleakError(f"Failed to read RSSI: {error}")
            future.set_exception(exception)
        else:
            future.set_result(rssi)

    def did_update_name(self, peripheral: CBPeripheralType, name: NSString) -> None:
        logger.debug(f"name of {peripheral.identifier()} changed to {name}")

    def did_modify_services(
        self, peripheral: CBPeripheralType, invalidated_services: NSArray
    ) -> None:
        logger.debug(
            f"{peripheral.identifier()} invalidated services: {invalidated_services}"
        )

    # ----------------------------------------------------------------------------------------------
    # Protocol Functions

    def create_delegate(self):

        def peripheral_didDiscoverServices_(_self, _cmd, pe_id, err_id):
            logger.info("peripheral_didDiscoverServices_")
            peripheral = ObjCInstance(pe_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            logger.info("services: %s", peripheral.services())
            logger.info("error: %s", err_id)
            self._event_loop.call_soon_threadsafe(
                self.did_discover_services,
                peripheral,
                peripheral.services(),
                error,
            )

        def peripheral_didDiscoverCharacteristicsForService_error_(
            _self, _cmd, pe_id, sv_id, err_id
        ):
            logger.debug("peripheral_didDiscoverCharacteristicsForService_error_")
            peripheral = ObjCInstance(pe_id)
            service = ObjCInstance(sv_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_discover_characteristics_for_service,
                peripheral,
                service,
                service.characteristics(),
                error,
            )

        def peripheral_didDiscoverDescriptorsForCharacteristic_error_(
            _self,
            _cmd,
            pe_id,
            ch_id,
            err_id,
        ):
            logger.debug("peripheral_didDiscoverDescriptorsForCharacteristic_error_")
            peripheral = ObjCInstance(pe_id)
            characteristic = ObjCInstance(ch_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_discover_descriptors_for_characteristic,
                peripheral,
                characteristic,
                error,
            )

        def peripheral_didUpdateValueForCharacteristic_error_(
            _self,
            _cmd,
            pe_id,
            ch_id,
            err_id,
        ):
            logger.debug("peripheral_didUpdateValueForCharacteristic_error_")
            peripheral = ObjCInstance(pe_id)
            characteristic = ObjCInstance(ch_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_update_value_for_characteristic,
                peripheral,
                characteristic,
                characteristic.value(),
                error,
            )

        def peripheral_didUpdateValueForDescriptor_error_(
            _self,
            _cmd,
            pe_id,
            desc_id,
            err_id,
        ):
            logger.debug("peripheral_didUpdateValueForDescriptor_error_")
            peripheral = ObjCInstance(pe_id)
            descriptor = ObjCInstance(desc_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_update_value_for_descriptor,
                peripheral,
                descriptor,
                descriptor.value(),
                error,
            )

        def peripheral_didWriteValueForCharacteristic_error_(
            _self,
            _cmd,
            pe_id,
            ch_id,
            err_id,
        ):
            logger.debug("peripheral_didWriteValueForCharacteristic_error_")
            peripheral = ObjCInstance(pe_id)
            characteristic = ObjCInstance(ch_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_write_value_for_characteristic,
                peripheral,
                characteristic,
                error,
            )

        def peripheral_didWriteValueForDescriptor_error_(
            _self, _cmd, pe_id, desc_id, err_id
        ):
            logger.debug("peripheral_didWriteValueForDescriptor_error_")
            peripheral = ObjCInstance(pe_id)
            descriptor = ObjCInstance(desc_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_write_value_for_descriptor,
                peripheral,
                descriptor,
                error,
            )

        def peripheral_didUpdateNotificationStateForCharacteristic_error_(
            _self, _cmd, pe_id, ch_id, err_id
        ):
            logger.debug(
                "peripheral_didUpdateNotificationStateForCharacteristic_error_"
            )
            peripheral = ObjCInstance(pe_id)
            characteristic = ObjCInstance(ch_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_update_notification_for_characteristic,
                peripheral,
                characteristic,
                error,
            )

        def peripheralDidUpdateName_(_self, _cmd, pe_id):
            logger.debug("peripheralDidUpdateName_")
            peripheral = ObjCInstance(pe_id)
            self._event_loop.call_soon_threadsafe(
                self.did_update_name, peripheral, peripheral.name()
            )

        def peripheral_didModifyServices_(_self, _cmd, pe_id, invsv_id):
            logger.debug("peripheral_didModifyServices_")
            peripheral = ObjCInstance(pe_id)
            invalidatedServices = ObjCInstance(invsv_id)
            self._event_loop.call_soon_threadsafe(
                self.did_modify_services, peripheral, invalidatedServices
            )

        def peripheral_didReadRSSI_error_(_self, _cmd, pe_id, rssi_id, err_id):
            logger.debug("peripheral_didReadRSSI_error_")
            peripheral = ObjCInstance(pe_id)
            rssi = ObjCInstance(rssi_id)
            error = ObjCInstance(err_id) if err_id is not None else None
            self._event_loop.call_soon_threadsafe(
                self.did_read_rssi, peripheral, rssi, error
            )

        methods = [
            peripheral_didDiscoverServices_,
            peripheral_didDiscoverCharacteristicsForService_error_,
            peripheral_didDiscoverDescriptorsForCharacteristic_error_,
            peripheral_didUpdateValueForCharacteristic_error_,
            peripheral_didUpdateValueForDescriptor_error_,
            peripheral_didWriteValueForCharacteristic_error_,
            peripheral_didWriteValueForDescriptor_error_,
            peripheral_didUpdateNotificationStateForCharacteristic_error_,
            peripheralDidUpdateName_,
            peripheral_didModifyServices_,
            peripheral_didReadRSSI_error_,
        ]

        peripheral_delegate_class = create_objc_class(
            "peripheral_delegate_class",
            methods=methods,
            protocols="CBPeripheralDelegate",
        )
        delegate_instance = peripheral_delegate_class.alloc().init()

        return delegate_instance
