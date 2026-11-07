"""
BLE Client for Pythonista3 on iOS

Created on 2019-06-26 by kevincar <kevincarrolldavis@gmail.com>

Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

import asyncio
import functools
import logging
from typing import Any, Optional, Set, Union

from bleak import BleakScanner
from bleak.args import SizedBuffer
from bleak.args.corebluetooth import CBStartNotifyArgs
from bleak.assigned_numbers import gatt_char_props_to_strs
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.client import BaseBleakClient, NotifyCallback
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTService, BleakGATTServiceCollection
from bleak.exc import BleakDeviceNotFoundError, BleakError
from objc_util import NSArray, NSData, ObjCInstance, nsdata_to_bytes

from .objc_types import (
    CBUUID,
    CBCharacteristicWriteWithoutResponse,
    CBCharacteristicWriteWithResponse,
    CBPeripheralStateConnected,
    CBPeripheralType,
)
from .PeripheralDelegate import PeripheralManager
from .scanner import BleakScannerPythonista3
from .utils import cb_uuid_to_str, descriptor_value_to_bytearray, nsnumber_to_int

logger = logging.getLogger(__name__)


class BleakClientPythonista3(BaseBleakClient):
    """Pythonista3 class interface for BleakClient

    Args:
        address_or_ble_device (`BLEDevice` or str): The Bluetooth address of the BLE peripheral to connect to or the `BLEDevice` object representing it.
        services: Optional set of service UUIDs that will be used.

    Keyword Args:
        timeout (float): Timeout for required ``BleakScanner.find_device_by_address`` call. Defaults to 10.0.

    """

    def __init__(
        self,
        address_or_ble_device: Union[BLEDevice, str],
        services: Optional[Set[str]] = None,
        **kwargs,
    ):
        super(BleakClientPythonista3, self).__init__(address_or_ble_device, **kwargs)

        self._peripheral: Optional[CBPeripheralType] = None
        self._manager = None
        self._central_manager = None

        if isinstance(address_or_ble_device, BLEDevice):
            (
                self._peripheral,
                self._central_manager,
            ) = address_or_ble_device.details

        self._requested_services = (
            NSArray.alloc().initWithArray_(list(map(CBUUID.UUIDWithString_, services)))
            if services
            else None
        )

    def __str__(self):
        return "BleakClientPythonista3 ({})".format(self.address)

    async def connect(self, pair: bool, **kwargs: Any) -> None:
        """Connect to a specified Peripheral

        Args:
            pair (bool): Ignored, since CoreBluetooth has no explicit pairing API.

        Keyword Args:
            timeout (float): Timeout for required ``BleakScanner.find_device_by_address`` call. Defaults to 10.0.

        """
        if pair:
            logger.debug("Explicit pairing is not available in CoreBluetooth.")

        timeout = kwargs.get("timeout", self._timeout)
        if self._peripheral is None:
            device = await BleakScanner.find_device_by_address(
                self.address, timeout=timeout, backend=BleakScannerPythonista3
            )

            if device:
                self._peripheral, self._central_manager = device.details
            else:
                raise BleakDeviceNotFoundError(
                    self.address, f"Device with address {self.address} was not found"
                )

        if self._manager is None:
            self._manager = PeripheralManager(self._peripheral)

        def disconnect_callback():
            # Ensure that `_get_services` retrieves services again, rather
            # than using the cached object
            self.services = None

            # If there are any pending futures waiting for delegate callbacks, we
            # need to raise an exception since the callback will no longer be
            # called because the device is disconnected.
            for future in self._manager.futures():
                try:
                    future.set_exception(BleakError("disconnected"))
                except asyncio.InvalidStateError:
                    # the future was already done
                    pass

            if self._disconnected_callback:
                self._disconnected_callback()

        manager = self._central_manager
        logger.debug("CentralManager at {}".format(manager))
        logger.debug("Connecting to BLE device @ {}".format(self.address))
        await manager.connect(self._peripheral, disconnect_callback, timeout=timeout)

        # Now get services
        logger.info("now get services")
        await self._get_services()
        logger.info("now I've got services")

    async def disconnect(self) -> None:
        """Disconnect from the peripheral device"""
        if (
            self._peripheral is None
            or self._peripheral.state() != CBPeripheralStateConnected
        ):
            return

        await self._central_manager.disconnect(self._peripheral)

    @property
    def is_connected(self) -> bool:
        """Checks for current active connection"""
        return (
            False
            if self._peripheral is None
            else self._peripheral.state() == CBPeripheralStateConnected
        )

    @property
    def name(self) -> str:
        """Get the name of the connected peripheral"""
        if self._peripheral is None:
            raise BleakError("Not connected")
        return str(self._peripheral.name())

    @property
    def mtu_size(self) -> int:
        """Get ATT MTU size for active connection"""
        # Use type CBCharacteristicWriteWithoutResponse to get maximum write
        # value length based on the negotiated ATT MTU size. Add the ATT header
        # length (+3) to get the actual ATT MTU size.
        return (
            self._peripheral.maximumWriteValueLengthForType_(
                CBCharacteristicWriteWithoutResponse
            )
            + 3
        )

    async def pair(self, *args: Any, **kwargs: Any) -> None:
        """Attempt to pair with a peripheral.

        .. note::

            This is not available on macOS since there is not explicit method to do a pairing, Instead the docs
            state that it "auto-pairs" when trying to read a characteristic that requires encryption, something
            Bleak cannot do apparently.

        Reference:

            - `Apple Docs <https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/BestPracticesForSettingUpYourIOSDeviceAsAPeripheral/BestPracticesForSettingUpYourIOSDeviceAsAPeripheral.html#//apple_ref/doc/uid/TP40013257-CH5-SW1>`_
            - `Stack Overflow post #1 <https://stackoverflow.com/questions/25254932/can-you-pair-a-bluetooth-le-device-in-an-ios-app>`_
            - `Stack Overflow post #2 <https://stackoverflow.com/questions/47546690/ios-bluetooth-pairing-request-dialog-can-i-know-the-users-choice>`_

        """
        raise NotImplementedError("Pairing is not available in Core Bluetooth.")

    async def unpair(self) -> None:
        """Remove pairing information for a peripheral."""
        raise NotImplementedError("Pairing is not available in Core Bluetooth.")

    async def _get_services(self) -> BleakGATTServiceCollection:
        """Get all services registered for this GATT server.

        Returns:
           A :py:class:`bleak.backends.service.BleakGATTServiceCollection` with this device's services tree.

        """
        if self.services is not None:
            return self.services

        services = BleakGATTServiceCollection()

        logger.info("Retrieving services...%s", self._requested_services)
        assert self._manager is not None
        cb_services_id = await self._manager.discover_services(self._requested_services)
        logger.info("got services")

        cb_services = [ObjCInstance(x) for x in cb_services_id]

        for service in cb_services:
            # N.B. the `startHandle` method of the CBService is an undocumented Core Bluetooth feature,
            # which Bleak takes advantage of in order to have a service handle to use.
            serv = BleakGATTService(
                service,
                nsnumber_to_int(service.startHandle()),
                cb_uuid_to_str(service.UUID()),
            )
            services.add_service(serv)

            serviceUUID = service.UUID().UUIDString()
            logger.info("Retrieving characteristics for service {}".format(serviceUUID))
            characteristics = await self._manager.discover_characteristics(service)

            for characteristic in characteristics:
                cUUID = characteristic.UUID().UUIDString()
                logger.debug(
                    "Retrieving descriptors for characteristic {}".format(cUUID)
                )

                char = BleakGATTCharacteristic(
                    characteristic,
                    nsnumber_to_int(characteristic.handle()),
                    cb_uuid_to_str(characteristic.UUID()),
                    list(gatt_char_props_to_strs(characteristic.properties())),
                    functools.partial(
                        self._peripheral.maximumWriteValueLengthForType_,
                        CBCharacteristicWriteWithoutResponse,
                    ),
                    serv,
                )
                services.add_characteristic(char)

                descriptors = await self._manager.discover_descriptors(characteristic)
                for descriptor in descriptors:
                    desc = BleakGATTDescriptor(
                        descriptor,
                        nsnumber_to_int(descriptor.handle()),
                        cb_uuid_to_str(descriptor.UUID()),
                        char,
                    )
                    services.add_descriptor(desc)
        logger.debug("Services resolved for %s", str(self))
        self.services = services
        return self.services

    async def read_gatt_char(
        self,
        characteristic: BleakGATTCharacteristic,
        *,
        use_cached: bool = False,
        **kwargs: Any,
    ) -> bytearray:
        """Perform read operation on the specified GATT characteristic.

        Args:
            characteristic (BleakGATTCharacteristic): The characteristic to read from.
            use_cached (bool): `False` forces macOS to read the value from the
                device again and not use its own cached value. Defaults to `False`.

        Returns:
            (bytearray) The read data.

        """
        assert self._manager is not None
        output = await self._manager.read_characteristic(
            characteristic.obj, use_cached=use_cached
        )
        value = bytearray(nsdata_to_bytes(output))
        logger.debug("Read Characteristic {0} : {1}".format(characteristic.uuid, value))
        return value

    async def read_gatt_descriptor(
        self,
        descriptor: BleakGATTDescriptor,
        *,
        use_cached: bool = False,
        **kwargs: Any,
    ) -> bytearray:
        """Perform read operation on the specified GATT descriptor.

        Args:
            descriptor (BleakGATTDescriptor): The descriptor to read from.
            use_cached (bool): `False` forces Windows to read the value from the
                device again and not use its own cached value. Defaults to `False`.

        Returns:
            (bytearray) The read data.
        """
        assert self._manager is not None
        output = await self._manager.read_descriptor(
            descriptor.obj, use_cached=use_cached
        )
        value = descriptor_value_to_bytearray(output, descriptor.uuid)
        logger.debug("Read Descriptor {0} : {1}".format(descriptor.handle, value))
        return value

    async def write_gatt_char(
        self,
        characteristic: BleakGATTCharacteristic,
        data: SizedBuffer,
        response: bool,
    ) -> None:
        # objc_util passes this argument as c_void_p, which rejects a bytearray.
        value = NSData.alloc().initWithBytes_length_(bytes(data), len(data))
        assert self._manager is not None
        await self._manager.write_characteristic(
            characteristic.obj,
            value,
            (
                CBCharacteristicWriteWithResponse
                if response
                else CBCharacteristicWriteWithoutResponse
            ),
        )
        logger.debug(f"Write Characteristic {characteristic.uuid} : {data}")

    async def write_gatt_descriptor(
        self, descriptor: BleakGATTDescriptor, data: SizedBuffer
    ) -> None:
        """Perform a write operation on the specified GATT descriptor.

        Args:
            descriptor: The descriptor to write to.
            data: The data to send (any bytes-like object).

        """
        value = NSData.alloc().initWithBytes_length_(bytes(data), len(data))
        assert self._manager is not None
        await self._manager.write_descriptor(descriptor.obj, value)
        logger.debug("Write Descriptor {0} : {1}".format(descriptor.handle, data))

    async def start_notify(
        self,
        characteristic: BleakGATTCharacteristic,
        callback: NotifyCallback,
        **kwargs: Any,
    ) -> None:
        """
        Activate notifications/indications on a characteristic.
        """
        assert self._manager is not None

        cb: CBStartNotifyArgs = kwargs["cb"]

        await self._manager.start_notifications(
            characteristic.obj,
            callback,
            cb.get("notification_discriminator"),
        )

    async def stop_notify(self, characteristic: BleakGATTCharacteristic) -> None:
        """Deactivate notification/indication on a specified characteristic.

        Args:
            characteristic (BleakGATTCharacteristic): The characteristic to deactivate
                notification/indication on.

        """
        assert self._manager is not None
        await self._manager.stop_notifications(characteristic.obj)

    async def get_rssi(self) -> int:
        """To get RSSI value in dBm of the connected Peripheral"""
        assert self._manager is not None
        return await self._manager.read_rssi()
