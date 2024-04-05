# -*- coding: utf-8 -*-
# ************************************************************
#
#     ble.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
BLE scanner (including specific functions for each supported OS)

Scan toio Core Cubes with internal BLE interface.
"""

import functools
import platform

from typing_extensions import Any, List, NamedTuple, Optional, Set

from toio.device_interface import (
    DEFAULT_SCAN_TIMEOUT,
    CubeInfo,
    ScannerInterface,
    SortKey,
)
from toio.device_interface.ble import BaseBleScanner
from toio.logger import get_toio_logger

logger = get_toio_logger(__name__)


class PlatformParam(NamedTuple):
    platform: str = "UNKNOWN"
    unsupported_result: Any = None


def async_platform_specified(param: PlatformParam = PlatformParam("UNKNOWN", None)):
    def platform_specified_wrapper(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if platform.system() == param.platform:
                result = await func(*args, **kwargs)
                return result
            else:
                logger.warning("platform '%s' is not supported", platform.system())
                return param.unsupported_result

        return wrapper

    return platform_specified_wrapper


class UniversalBleScanner(ScannerInterface):
    async def _scan(
        self,
        num: Optional[int] = None,
        cube_id: Optional[Set[str]] = None,
        address: Optional[Set[str]] = None,
        sort: SortKey = None,
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> List[CubeInfo]:
        scanner = BaseBleScanner()
        return await scanner._scan(
            num=num, cube_id=cube_id, address=address, sort=sort, timeout=timeout
        )

    async def scan( # type: ignore
        self, num: int, sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
    ) -> List[CubeInfo]:
        """Scan the specified number of toio Core Cubes.

        The scan is terminated by a timeout.
        In the case of a timeout, the number of elements in the returned list
        is the number of cubes found at the time of the timeout.

        Args:
            num (int): Number of cubes to be found.
            sort (SortKey, optional): Key to sort results. Defaults to "rssi".
            timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

        Returns:
            List[Tuple[BLEDevice, AdvertisementData]]: List of found cubes.
        """
        return await self._scan(num=num, sort=sort, timeout=timeout)

    async def scan_with_id(
        self,
        cube_id: Set[str],
        sort: SortKey = "rssi",
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> List[CubeInfo]:
        """Scan toio Core Cubes with specified id.

        The scan is terminated by a timeout.
        In the case of a timeout, the number of elements in the returned list
        is the number of cubes found at the time of the timeout.

        Args:
            cube_id (set[str]): Set of cube id to be found.
            sort (SortKey, optional): Key to sort results. Defaults to "rssi".
            timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

        Returns:
            List[Tuple[BLEDevice, AdvertisementData]]: List of found cubes.
        """
        return await self._scan(cube_id=cube_id, sort=sort, timeout=timeout)

    async def scan_with_address(
        self,
        address: Set[str],
        sort: SortKey = "rssi",
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> List[CubeInfo]:
        """Scan toio Core Cubes with specified BLE address.

        The scan is terminated by a timeout.
        In the case of a timeout, the number of elements in the returned list
        is the number of cubes found at the time of the timeout.

        Args:
            address (set[str]): Set of BLE address to be found.
            sort (SortKey, optional): Key to sort results. Defaults to "rssi".
            timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

        Returns:
            List[Tuple[BLEDevice, AdvertisementData]]: List of found cubes.
        """
        return await self._scan(address=address, sort=sort, timeout=timeout)

    @async_platform_specified(PlatformParam("Windows", []))
    async def scan_registered_cubes(
        self, num: int, sort: SortKey = "rssi", timeout: float = DEFAULT_SCAN_TIMEOUT
    ) -> List[CubeInfo]:
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
            List[Tuple[BLEDevice, AdvertisementData]]: List of found cubes.
        """
        from toio.scanner.platform.windows_ble import get_registered_cubes

        registered_cubes = get_registered_cubes()
        addresses = {x.address.upper() for x in registered_cubes}
        found = await self.scan_with_address(addresses, sort, timeout)
        if len(found) > num:
            return found[:num]
        else:
            return found

    @async_platform_specified(PlatformParam("Windows", []))
    async def scan_registered_cubes_with_id(
        self,
        cube_id: Set[str],
        sort: SortKey = "rssi",
        timeout: float = DEFAULT_SCAN_TIMEOUT,
    ) -> List[CubeInfo]:
        """Scan toio Core Cube specified by the cube_id registered with Windows

        This function only works on Windows platform.
        On the other platform, this function always returns empty list.

        Args:
            cube_id (set[str]): Set of cube id to be found.
            sort (SortKey, optional): Key to sort results. Defaults to "rssi".
            timeout (float, optional): Scan timeout. Defaults to DEFAULT_SCAN_TIMEOUT.

        Returns:
            List[Tuple[BLEDevice, AdvertisementData]]: List of found cubes.
        """
        from toio.scanner.platform.windows_ble import get_registered_cubes

        registered_cubes = get_registered_cubes()
        address_list = set([])
        for cube in registered_cubes:
            for id_str in cube_id:
                if id_str in cube.name:
                    address_list.add(cube.address.upper())
        if len(address_list) == 0:
            return []
        else:
            found = await self.scan_with_address(address_list, sort, timeout)
            return found
