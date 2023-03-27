# -*- coding: utf-8 -*-
# ************************************************************
#
#     position.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************
"""
Utility functions for cube position and cube location.
"""

from __future__ import annotations

import math
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union

MATRECT_DEFAULT_X = 65535
MATRECT_DEFAULT_Y = 65535

STAY_CURRENT = 0xFFFF


@dataclass
class Point:
    """
    A point on 2 dimensions
    """

    x: int = 0
    y: int = 0

    @staticmethod
    def new() -> Point:
        return Point(x=0, y=0)

    def __add__(self, other: Point) -> Point:
        return Point(x=(self.x + other.x), y=(self.y + other.y))

    def __sub__(self, other: Point) -> Point:
        return Point(x=(self.x - other.x), y=(self.y - other.y))

    def __lt__(self, other: Point) -> bool:
        return self.x < other.x and self.y < other.y

    def __le__(self, other: Point) -> bool:
        return self.x <= other.x and self.y <= other.y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x != other.x or self.y != other.y

    def __gt__(self, other: Point) -> bool:
        return self.x >= other.x or self.y >= other.y

    def __ge__(self, other: Point) -> bool:
        return self.x > other.x or self.y > other.y

    def __mul__(self, mul: float) -> Point:
        return Point(x=round(self.x * mul), y=round(self.y * mul))

    def __truediv__(self, div: float) -> Point:
        return Point(x=round(self.x / div), y=round(self.y / div))

    def __floordiv__(self, div: float) -> Point:
        return Point(x=round(self.x // div), y=round(self.y // div))

    def distance(self, other: Point) -> float:
        diff = self - other
        return math.sqrt((diff.x * diff.x) + (diff.y * diff.y))

    def flatten(self):
        return self.x, self.y


@dataclass
class CubeLocation:
    """
    A Position and angle of a cube on 2 dimensions
    """

    point: Point
    """
    Point of a cube
    """
    angle: int = 0
    """
    Angle of a cube (degree)
    """

    @staticmethod
    def new() -> CubeLocation:
        return CubeLocation(
            point=Point.new(),
            angle=0,
        )

    def __add__(self, other: CubeLocation) -> CubeLocation:
        point = self.point + other.point
        angle = (self.angle + other.angle) % 360
        return CubeLocation(point=point, angle=angle)

    def __sub__(self, other: CubeLocation) -> CubeLocation:
        point = self.point - other.point
        angle = self.angle - (other.angle % 360)
        if angle < 0:
            angle += 360
        return CubeLocation(point=point, angle=angle)

    def get_boundary_point(self, target: CubeLocation) -> CubeLocation:
        """
        Obtains the point where a line passing through two points
        intersects the coordinate axis in the first quadrant.
        """
        x = target.point.x
        y = target.point.y
        diff = target.point - self.point

        # Find the point that intersects the y-axis
        if x < 0:
            x = 0
            y = round(self.point.y - ((diff.y / diff.x) * self.point.x))

        # If 'y' is not in the first quadrant, find the point that intersects the x-axis
        if y < 0:
            x = round(self.point.x - ((diff.x / diff.y) * self.point.y))
            y = 0

        assert x >= 0
        assert y >= 0
        return CubeLocation(point=Point(x=x, y=y), angle=target.angle)

    def flatten(self):
        return self.point.flatten() + (self.angle,)


@dataclass
class MatRect:
    """
    A toio mat
    """

    top_left: Point
    """
    Top-left point of a mat
    """
    bottom_right: Point
    """
    Bottom-right point of a mat
    """
    name: Optional[str] = None
    """
    Mat name
    """

    @staticmethod
    def new() -> MatRect:
        return MatRect(
            top_left=Point(x=0, y=0),
            bottom_right=Point(MATRECT_DEFAULT_X, MATRECT_DEFAULT_Y),
            name=None,
        )

    def center(self) -> Point:
        return self.top_left + ((self.bottom_right - self.top_left) / 2)

    def __contains__(self, x: Point):
        return self.top_left <= x <= self.bottom_right

    def __str__(self) -> str:
        return f"{self.name}: ({self.top_left.x}, {self.top_left.y}) - ({self.bottom_right.x}, {self.bottom_right.y})"

    def flatten(self):
        return self.top_left.flatten() + self.bottom_right.flatten()


class CoordinateSystemABC(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, origin: Point = Point(x=0, y=0)):
        self.native_origin = origin
        raise NotImplementedError()

    @abstractmethod
    def set_origin(self, origin: Point) -> None:
        raise NotImplementedError()

    @abstractmethod
    def to_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    @abstractmethod
    def to_native_x(self, x: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    @abstractmethod
    def to_native_y(self, y: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    @abstractmethod
    def from_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    @abstractmethod
    def from_native_x(self, x: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    @abstractmethod
    def from_native_y(self, y: Union[int, float]) -> Union[int, float]:
        raise NotImplementedError()

    def to_native_point(self, pos: Point) -> Point:
        return Point(
            x=round(self.to_native_x(pos.x)),
            y=round(self.to_native_y(pos.y)),
        )

    def to_native_location(self, location: CubeLocation) -> CubeLocation:
        return CubeLocation(
            point=self.to_native_point(location.point),
            angle=round(self.to_native_angle(location.angle)),
        )

    def from_native_point(self, pos: Point) -> Point:
        return Point(
            x=round(self.from_native_x(pos.x)),
            y=round(self.from_native_y(pos.y)),
        )

    def from_native_location(self, location: CubeLocation) -> CubeLocation:
        return CubeLocation(
            point=self.from_native_point(location.point),
            angle=round(self.from_native_angle(location.angle)),
        )


class DefaultCoordinateSystem(CoordinateSystemABC):
    """
    Default coordinate system

    No coordinate transformation
    No angle transformation
    """

    def __init__(self, origin: Point):
        self.native_origin = origin

    def set_origin(self, origin: Point) -> None:
        self.native_origin = origin

    def to_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        return angle

    def to_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x

    def to_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return y

    def from_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        return angle

    def from_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x

    def from_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return y


@dataclass
class RelativeCubeLocation:
    """
    Location of the cube in the relative coordinate system
    """

    relative_location: CubeLocation
    """
    Relative location of a cube
    """
    coordinate_system: CoordinateSystemABC
    """
    Coordinate system
    """

    @staticmethod
    def new() -> RelativeCubeLocation:
        """
        Create new RelativeCubeLocation

        Returns:
            RelativeCubeLocation: new relative cube location instance
        """
        return RelativeCubeLocation(
            relative_location=CubeLocation.new(),
            coordinate_system=DefaultCoordinateSystem(origin=Point(x=0, y=0)),
        )

    def to_absolute_point(self) -> Point:
        """
        Get the point of the cube on the absolute coordinate system

        Returns:
            Point: Point of the absolute coordinate system
        """
        return self.coordinate_system.to_native_point(self.relative_location.point)

    def to_absolute_location(self) -> CubeLocation:
        """
        Get the location of the cube on the absolute coordinate system

        Returns:
            CubeLocation: CubeLocation of the absolute coordinate system
        """
        return self.coordinate_system.to_native_location(self.relative_location)

    def from_absolute_point(self, abs_point: Point) -> Point:
        """
        Set the relative point from the absolute point

        Args:
            abs_point (CubePoint): Point on the absolute coordinate system

        Returns:
            Point: Point on the relative coordinate system
        """
        self.relative_location.point = self.coordinate_system.from_native_point(
            abs_point
        )
        return self.relative_location.point

    def from_absolute_location(self, abs_location: CubeLocation) -> CubeLocation:
        """
        Set the relative location from the absolute location

        Args:
            abs_location (CubeLocation): Location on the absolute coordinate system

        Returns:
            CubeLocation: Location on the relative coordinate system
        """
        self.relative_location = self.coordinate_system.from_native_location(
            abs_location
        )
        return self.relative_location

    def change_coordinate_system(
        self, new_coordinate_system: CoordinateSystemABC
    ) -> None:
        """
        Change the coordinate system
        The location is updated to the coordinates in the new coordinate system
        """
        abs_location = self.to_absolute_location()
        self.coordinate_system = new_coordinate_system
        self.relative_location = self.coordinate_system.from_native_location(
            abs_location
        )


class ToioMat(object):
    """
    Definitions of official toio mats
    """

    ToioCollectionMatRing = MatRect(
        top_left=Point(x=45, y=45),
        bottom_right=Point(x=455, y=455),
        name="Toio Collection (ring)",
    )
    ToioCollectionMatColoredTiles = MatRect(
        top_left=Point(x=545, y=45),
        bottom_right=Point(x=955, y=455),
        name="Toio Collection (colored tiles)",
    )
    PicotonsPlayMatFront = MatRect(
        top_left=Point(x=59, y=2088),
        bottom_right=Point(x=437, y=2285),
        name="Picotons (front)",
    )
    PicotonsPlayMatBack = MatRect(
        top_left=Point(x=59, y=2303),
        bottom_right=Point(x=437, y=2499),
        name="Picotons (back)",
    )
    PicotonsControlMat = MatRect(
        top_left=Point(x=764, y=2093),
        bottom_right=Point(x=953, y=2290),
        name="Picotons (control)",
    )
    PicotonsAutoplayMat = MatRect(
        top_left=Point(x=554, y=2093),
        bottom_right=Point(x=742, y=2290),
        name="Picotons (auto play)",
    )
    SimpleMat = MatRect(
        top_left=Point(x=98, y=142),
        bottom_right=Point(x=402, y=358),
        name="Simple mat",
    )
    GesundroidMat = MatRect(
        top_left=Point(x=1050, y=45),
        bottom_right=Point(x=1460, y=455),
        name="Gesundroid",
    )

    mats = (
        ToioCollectionMatRing,
        ToioCollectionMatColoredTiles,
        PicotonsPlayMatFront,
        PicotonsPlayMatBack,
        PicotonsControlMat,
        PicotonsAutoplayMat,
        SimpleMat,
        GesundroidMat,
    )
