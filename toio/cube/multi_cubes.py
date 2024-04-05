# -*- coding: utf-8 -*-
# ************************************************************
#
#     multi_cubes.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

import asyncio

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

from ..device_interface import CubeInfo, ScannerInterface
from ..logger import get_toio_logger
from ..scanner.ble import UniversalBleScanner

if TYPE_CHECKING:
    from ..cube import ToioCoreCube

logger = get_toio_logger(__name__)


class MultipleToioCoreCubes:
    """
    Multiple cube control class

    This class is a wrapper to control multiple cubes more easier.

    When MultipleCubes is initialized with an integer, the scan() function
    can search for a specified number of cubes.
    scan() can be followed by a call to the connect() function to connect
    to multiple cubes.

    If you initialize MultipleCubes with a list of CubeInfo,
    you can connect to multiple cubes by calling the connect() function.
    In this case, the scan() function does not work.

    MultipleCubes is an asynchronous context manager.
    When 'async with' is used, '__aenter__' handles the process up to connection,
    and '__aexit__' handles the disconnection.

    Access to each cubes

    Each cube can be accessed by the number.

    >>> async with MultipleToioCoreCubes(2) as cubes:
    >>>    cubes[0].api....()
    >>>    cubes[1].api....()

    Each cube can be accessd by 'for' also.

    >>> async with MultipleToioCoreCubes(2) as cubes:
    >>>    for c in cubes:
    >>>       c.api....()

    When 'names' is specified, cubes has each name and can be accessed with specified name.

    >>> # accessing by cube name property
    >>> async with MultipleToioCoreCubes(2, "alpha", "beta") as cubes:
    >>>    cubes.alpha.api....()
    >>>    cubes.beta.api....()

    >>> # accessing cubes using the cube interface obtained by name
    >>> async with MultipleToioCoreCubes(2, "alpha", "beta") as cubes:
    >>>     alpha = cubes.named("alpha")
    >>>     beta = cubes.named("beta")
    >>>     alpha.api....()
    >>>     beta.api....()

    """

    def __init__(
        self,
        cubes: Union[int, List[CubeInfo]],
        names: Optional[Sequence[str]] = None,
        scanner: Type[ScannerInterface] = UniversalBleScanner,
        scanner_args: Sequence[Any] = (),
    ):
        """
        Initialize MultipleCubes

        Args:
            cubes (Union[int, List[CubeInfo]]): number of cubes to be scanned, or list of cubes to be handled
            names (Optional[Sequence[str]]): sequence of names of cubes
            scanner (Type[ScannerInterface]): scanner interface (default is UniversalBleScanner)
            scanner_args (Sequence[Any]): arguments given to the scanner.scan() function
        """
        from ..cube import ToioCoreCube

        self._cube_num: Optional[int] = None
        self._cubes: List[ToioCoreCube] = []
        if isinstance(cubes, int):
            self._cube_num = cubes
            self._scanning_required = True
        else:
            self._scanning_required = False
            self._cubes = ToioCoreCube.create_cubes(cubes)

        self._names = names
        self._scanner = scanner
        self._scanner_args = scanner_args
        self._cube_dict: Dict[str, ToioCoreCube] = {}

    def __getattr__(self, name: str) -> Any:
        cube = self._cube_dict.get(name)
        if cube:
            return cube
        else:
            raise AttributeError("'%s' is not found" % name)

    async def __aenter__(self):
        await self.scan()
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    def __len__(self) -> int:
        return len(self._cubes)

    def __getitem__(self, n) -> ToioCoreCube:
        return self._cubes[n]

    def _assign_cubes(self):
        assert self._cubes is not None
        assert not isinstance(self._cubes, int)
        if self._names is not None:
            for name, cube in zip(self._names, self._cubes):
                self._cube_dict[name] = cube

    async def scan(self):
        """
        scan cubes

        If MultipleCubes is initialized with integer number,
        this function performs to scan the number of cubes.
        """
        from ..cube import ToioCoreCube

        if self._scanning_required and isinstance(self._cube_num, int):
            device_list = await self._scanner().scan(
                self._cube_num, *self._scanner_args
            )
            self._cubes = ToioCoreCube.create_cubes(device_list)
            self._scanning_required = False

    async def connect(self):
        """
        connect to multiple cubes
        """
        self._assign_cubes()
        connect_list = [cube.connect() for cube in self._cubes]
        result_list = await asyncio.gather(*connect_list)
        while False in result_list:
            logger.info("try to connect again")
            for i, result in enumerate(result_list):
                if result:
                    del connect_list[i]
            result_list = await asyncio.gather(*connect_list)

    async def disconnect(self):
        """
        disconnect to multiple cubes
        """
        disconnect_list = [cube.disconnect() for cube in self._cubes]
        result_list = await asyncio.gather(*disconnect_list)
        while False in result_list:
            logger.info("try to disconnect again")
            for i, result in enumerate(result_list):
                if result:
                    del disconnect_list[i]
            result_list = await asyncio.gather(*disconnect_list)

    def named(self, name: str) -> ToioCoreCube:
        """
        get the cube specified by the name

        Args:
            name (str): name

        Returns:
            ToioCoreCube:

        Exceptions:
            ValueError: the cube specified is not found
        """
        cube = self._cube_dict.get(name)
        if cube is not None:
            return cube
        else:
            raise ValueError("'%s' is not found" % name)
