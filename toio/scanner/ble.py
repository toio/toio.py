# -*- coding: utf-8 -*-
# ************************************************************
#
#     ble.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
BLE scanner

Scan toio Core Cubes with internal BLE interface.
"""

import platform

from toio.device_interface import DEFAULT_SCAN_TIMEOUT, CubeInfo, SortKey
from toio.device_interface.ble import BleScanner
from toio.logger import get_toio_logger

if platform.system() == "Windows":
    from toio.scanner.platform.windows_ble import get_registered_cubes

logger = get_toio_logger(__name__)


async def scan(
    num: int, sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
) -> list[CubeInfo]:
    """Scan the specified number of toio Core Cubes.

    The scan is terminated by a timeout.
    In the case of a timeout, the number of elements in the returned list
    is the number of cubes found at the time of the timeout.

    Args:
        num (int): Number of cubes to be found.
        sort (SortKey, optional): Key to sort results. Defaults to "rssi".
        timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

    Returns:
        list[tuple[BLEDevice, AdvertisementData]]: List of found cubes.
    """
    scanner = BleScanner()
    return await scanner.scan(num=num, sort=sort, timeout=timeout)


async def scan_with_id(
    cube_id: set[str], sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
) -> list[CubeInfo]:
    """Scan toio Core Cubes with specified id.

    The scan is terminated by a timeout.
    In the case of a timeout, the number of elements in the returned list
    is the number of cubes found at the time of the timeout.

    Args:
        cube_id (set[str]): Set of cube id to be found.
        sort (SortKey, optional): Key to sort results. Defaults to "rssi".
        timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

    Returns:
        list[tuple[BLEDevice, AdvertisementData]]: List of found cubes.
    """
    scanner = BleScanner()
    return await scanner.scan(cube_id=cube_id, sort=sort, timeout=timeout)


async def scan_with_address(
    address: set[str], sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
) -> list[CubeInfo]:
    """Scan toio Core Cubes with specified BLE address.

    The scan is terminated by a timeout.
    In the case of a timeout, the number of elements in the returned list
    is the number of cubes found at the time of the timeout.

    Args:
        address (set[str]): Set of BLE address to be found.
        sort (SortKey, optional): Key to sort results. Defaults to "rssi".
        timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

    Returns:
        list[tuple[BLEDevice, AdvertisementData]]: List of found cubes.
    """
    scanner = BleScanner()
    return await scanner.scan(address=address, sort=sort, timeout=timeout)


async def scan_registered_cubes(
    num: int, sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
) -> list[CubeInfo]:
    """Scan toio Core Cubes registered with Windows

    This function only works on Windows platform.
    On the other platform, this function always returns empty list.

    Even if `num` is greater than the number of registered cubes,
    the maximum size of the list returned by this function is the number of registered cubes.

    Args:
        num (int): Number of cubes to be found.
        sort (SortKey, optional): Key to sort results. Defaults to "rssi".
        timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

    Returns:
        list[tuple[BLEDevice, AdvertisementData]]: List of found cubes.
    """
    if platform.system() == "Windows":
        registered_cubes = get_registered_cubes()
        addresses = {x.address.upper() for x in registered_cubes}
        found = await scan_with_address(addresses, sort, timeout)
        if len(found) > num:
            return found[:num]
        else:
            return found
    else:
        logger.warning("platform '%s' is not supported", platform.system())
        return []


async def scan_registered_cubes_with_id(
    cube_id: set[str], sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
) -> list[CubeInfo]:
    """Scan toio Core Cube specified by the cube_id registered with Windows

    This function only works on Windows platform.
    On the other platform, this function always returns empty list.

    Args:
        cube_id (set[str]): Set of cube id to be found.
        sort (SortKey, optional): Key to sort results. Defaults to "rssi".
        timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

    Returns:
        list[tuple[BLEDevice, AdvertisementData]]: List of found cubes.
    """
    if platform.system() == "Windows":
        registered_cubes = get_registered_cubes()
        address_list = set([])
        for cube in registered_cubes:
            for id_str in cube_id:
                if id_str in cube.name:
                    address_list.add(cube.address.upper())
        if len(address_list) == 0:
            return []
        else:
            found = await scan_with_address(address_list, sort, timeout)
            return found
    else:
        logger.warning("platform '%s' is not supported", platform.system())
        return []
