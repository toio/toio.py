# -*- coding: utf-8 -*-
# ************************************************************
#
#     ble.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
BLE device interface
"""

import asyncio
from typing import Optional, Union
from uuid import UUID

from bleak import BleakClient, BleakScanner

from toio.device_interface import (
    DEFAULT_SCAN_TIMEOUT,
    AdvertisementData,
    BLEDevice,
    CubeDevice,
    CubeInfo,
    CubeInterface,
    GattNotificationHandler,
    GattReadData,
    GattWriteData,
    ScannerInterface,
    SortKey,
)
from toio.logger import get_toio_logger
from toio.toio_uuid import TOIO_UUID_SERVICE

RSSI_UNKNOWN = -65535

logger = get_toio_logger(__name__)


class BleCube(CubeInterface):
    """
    Cube interface for internal BLE interface.
    """

    def __init__(self, device: Union[CubeDevice, str]):
        self.connected: bool = False
        self.device = BleakClient(device)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self) -> bool:
        if not self.connected:
            self.connected = await self.device.connect()
            while not self.device.is_connected:
                await asyncio.sleep(0.1)
        else:
            logger.warning("already connected")
        return self.connected

    async def disconnect(self):
        if self.connected:
            await self.device.disconnect()
            while self.device.is_connected:
                await asyncio.sleep(0.1)
        else:
            logger.warning("already disconnected")

    async def read(self, char_uuid: UUID) -> GattReadData:
        return await self.device.read_gatt_char(char_uuid)

    async def write(self, char_uuid: UUID, data: GattWriteData, response: bool = False):
        await self.device.write_gatt_char(char_uuid, data, response)

    async def register_notification_handler(
        self, char_uuid: UUID, notification_handler: GattNotificationHandler
    ) -> bool:
        await self.device.start_notify(char_uuid, notification_handler)
        return True

    async def unregister_notification_handler(self, char_uuid: UUID) -> bool:
        await self.device.stop_notify(char_uuid)
        return True


class BleScanner(ScannerInterface):
    """BleScanner
    Scanner for internal BLE interface.
    """

    def __init__(self):
        pass

    async def scan(
        self,
        num: Optional[int] = None,
        cube_id: Optional[set[str]] = None,
        address: Optional[set[str]] = None,
        sort: SortKey = None,
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> list[CubeInfo]:
        """Scan toio Core Cubes.
        Argument 'num', 'cube_id', and 'address' is exclusive.

        Args:
            num (Optional[int], optional): Number of cubes to be found. Defaults to None.
            cube_id (Optional[set[str]], optional): Set of cube id to be found. Defaults to None.
            address (Optional[set[str]], optional): Set of cube BLE address to be found. Defaults to None.
            sort (SortKey, optional): Key to sort results. Defaults to None (no sort).
            timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

        Returns:
            list[CubeInfo]: List of found cubes

        Notes:
            If the cube named "31j" is found in scanning, this function warns it.
            If you specify the name "31j" to find the cube, this function warns it.

            "31j" is wrong name.
            This name appears when the toio Core Cube fall wrong state.
            To recover this, turn off the cube and back again.

            Ref: https://support.toio.io/s/article/15855
        """
        w31j = False
        condition_met = asyncio.Event()
        found_cubes: dict[Union[str, int], CubeInfo] = {}

        if cube_id is not None and "31j" in cube_id:
            logger.warning(
                "warning: scanner: Specifying cube_id '31j' is NOT recommended"
            )

        # detection callback
        def check_condition(device: BLEDevice, advertisement: AdvertisementData):
            service_uuids = map(UUID, advertisement.service_uuids)
            if TOIO_UUID_SERVICE in service_uuids:
                nonlocal w31j
                nonlocal condition_met
                nonlocal found_cubes
                if not w31j and device.name is not None and device.name.endswith("31j"):
                    logger.warning(
                        "warning: scanner: cube_id '31j' is found. Why not turn all cubes off and back again?"
                    )
                    w31j = True

                if address is not None:
                    address_list = [x.upper() for x in address]
                    if device.address in address_list:
                        found_cubes[device.address] = CubeInfo(
                            name=device.name,
                            device=device,
                            interface=BleCube(device),
                            advertisement=advertisement,
                        )
                    if len(found_cubes) >= len(address):
                        condition_met.set()
                elif cube_id is not None and device.name is not None:
                    for id_str in cube_id:
                        if id_str in device.name:
                            found_cubes[device.address] = CubeInfo(
                                name=device.name,
                                device=device,
                                interface=BleCube(device),
                                advertisement=advertisement,
                            )
                    if len(found_cubes) >= len(cube_id):
                        condition_met.set()
                else:
                    found_cubes[device.address] = CubeInfo(
                        name=device.name,
                        device=device,
                        interface=BleCube(device),
                        advertisement=advertisement,
                    )

        # scan ble devices
        async with BleakScanner(detection_callback=check_condition):
            try:
                await asyncio.wait_for(condition_met.wait(), timeout=timeout)
            except TimeoutError:
                logger.debug(f"scanner: timeout {timeout} sec")
            except Exception:
                raise

        # get the list of cubes
        toio_cubes = list(found_cubes.values())

        # sort
        if sort is not None and len(toio_cubes) >= 2:
            if sort == "rssi":

                def rssi(info: CubeInfo) -> int:
                    if info.advertisement.rssi is not None:
                        return info.advertisement.rssi
                    else:
                        return RSSI_UNKNOWN

                toio_cubes.sort(key=rssi, reverse=True)
            elif sort == "local_name":

                def local_name(info: CubeInfo) -> str:
                    if info.name is not None:
                        return info.name
                    else:
                        return ""

                toio_cubes.sort(key=local_name)
        if num is not None and len(toio_cubes) > num:
            return toio_cubes[:num]
        else:
            return toio_cubes
