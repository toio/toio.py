"""
Ported to Pythonista3 in 2024 by Sony Interactive Entertainment Inc.

"""

import logging
from typing import Any, Dict, List, Literal, Optional, TypedDict

from bleak.backends.scanner import (
    AdvertisementData,
    AdvertisementDataCallback,
    BaseBleakScanner,
)
from bleak.exc import BleakError
from objc_util import NSDictionary, nsdata_to_bytes

from .CentralManagerDelegate import CBPeripheralType, CentralManager
from .utils import cb_uuid_to_str

logger = logging.getLogger(__name__)


class CBScannerArgs(TypedDict, total=False):
    """
    Platform-specific :class:`BleakScanner` args for the Pythonista3 backend.
    """

    use_bdaddr: bool
    """
    If true, use Bluetooth address instead of UUID.

    .. warning:: This uses an undocumented IOBluetooth API to get the Bluetooth
        address and may break in the future macOS releases. `It is known to not
        work on macOS 10.15 <https://github.com/hbldh/bleak/issues/1286>`_.
    """


class BleakScannerPythonista3(BaseBleakScanner):
    """The iOS Bleak BLE Scanner for pythonista3.

    Documentation:
    https://developer.apple.com/documentation/corebluetooth/cbcentralmanager

    CoreBluetooth doesn't explicitly use Bluetooth addresses to identify peripheral
    devices because private devices may obscure their Bluetooth addresses. To cope
    with this, CoreBluetooth utilizes UUIDs for each peripheral. Bleak uses
    this for the BLEDevice address on macOS.

    Args:
        detection_callback:
            Optional function that will be called each time a device is
            discovered or advertising data has changed.
        service_uuids:
            Optional list of service UUIDs to filter on. Only advertisements
            containing this advertising data will be received.
        scanning_mode:
            Set to ``"passive"`` to avoid the ``"active"`` scanning mode. Not
            supported on macOS! Will raise :class:`BleakError` if set to
            ``"passive"``
        **timeout (float):
             The scanning timeout to be used, in case of missing
            ``stopScan_`` method.
    """

    def __init__(
        self,
        detection_callback: Optional[AdvertisementDataCallback],
        service_uuids: Optional[List[str]],
        scanning_mode: Literal["active", "passive"],
        *,
        cb: CBScannerArgs,
        **kwargs
    ):
        super().__init__(detection_callback, service_uuids)

        self._use_bdaddr = cb.get("use_bdaddr", False)

        if scanning_mode == "passive":
            raise BleakError("iOS does not support passive scanning")

        self._manager = CentralManager()
        self._timeout: float = kwargs.get("timeout", 5.0)

    async def start(self) -> None:
        self.seen_devices = {}

        def callback(p: CBPeripheralType, a: NSDictionary, r: int) -> None:

            # Process service data
            service_data_dict_raw = a["kCBAdvDataServiceData"]
            service_data = {}
            if service_data_dict_raw is not None:
                service_data_keys = service_data_dict_raw.allKeys()
                for key in service_data_keys:
                    service_data[cb_uuid_to_str(key)] = nsdata_to_bytes(
                        service_data_dict_raw[key]
                    )

            # Process manufacturer data into a more friendly format
            manufacturer_binary_data = a["kCBAdvDataManufacturerData"]
            manufacturer_data = {}
            if manufacturer_binary_data:
                binary_data = nsdata_to_bytes(manufacturer_binary_data)
                manufacturer_id = int.from_bytes(binary_data[0:2], byteorder="little")
                manufacturer_value = bytes(binary_data[2:])
                manufacturer_data[manufacturer_id] = manufacturer_value

            service_uuid_data = a["kCBAdvDataServiceUUIDs"]
            if service_uuid_data is None:
                service_uuid_data = []
            service_uuids = [cb_uuid_to_str(u) for u in service_uuid_data]

            # set tx_power data if available
            tx_power = a["kCBAdvDataTxPowerLevel"]
            if tx_power is not None:
                tx_power = tx_power.intValue()

            advertisement_data = AdvertisementData(
                local_name=str(a["kCBAdvDataLocalName"]),
                manufacturer_data=manufacturer_data,
                service_data=service_data,
                service_uuids=service_uuids,
                tx_power=tx_power,
                rssi=r,
                platform_data=(p, a, r),
            )

            if self._use_bdaddr:
                # HACK: retrieveAddressForPeripheral_ is undocumented but seems to do the trick
                address_bytes: bytes = (
                    self._manager.central_manager.retrieveAddressForPeripheral_(p)
                )
                address = address_bytes.hex(":").upper()
            else:
                address = cb_uuid_to_str(p.identifier())

            device = self.create_or_update_device(
                address,
                str(p.name()),
                (p, self._manager),
                advertisement_data,
            )

            self.call_detection_callbacks(device, advertisement_data)

        self._manager.callbacks[id(self)] = callback
        await self._manager.start_scan(self._service_uuids)

    async def stop(self) -> None:
        await self._manager.stop_scan()
        self._manager.callbacks.pop(id(self), None)

    def set_scanning_filter(self, **kwargs) -> None:
        """Set scanning filter for the scanner.

        .. note::

            This is not implemented for macOS yet.

        Raises:

           ``NotImplementedError``

        """
        raise NotImplementedError(
            "Need to evaluate which macOS versions to support first..."
        )

    # macOS specific methods

    @property
    def is_scanning(self):
        return self._manager.central_manager.isScanning()
