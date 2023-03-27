# -*- coding: utf-8 -*-
# ************************************************************
#
#     coordinate_systems.py
#
#     Copyright 2023 Sony Interactive Entertainment Inc.
#
# ************************************************************

from typing import Union

from toio.position import CoordinateSystemABC, Point


class ToioRelativeCoordinateSystem(CoordinateSystemABC):
    def __init__(self, origin: Point = Point(x=0, y=0)):
        self.native_origin = origin

    def set_origin(self, origin: Point) -> None:
        self.native_origin = origin

    def to_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        return angle % 360

    def to_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x + self.native_origin.x

    def to_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return y + self.native_origin.y

    def from_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        return angle

    def from_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x - self.native_origin.x

    def from_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return y - self.native_origin.y


class VisualProgrammingCoordinateSystem(CoordinateSystemABC):
    def __init__(self, origin: Point = Point(x=0, y=0)):
        self.native_origin = origin

    def set_origin(self, origin: Point) -> None:
        self.native_origin = origin

    def to_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        angle = angle % 360
        native_angle = angle + 270
        return native_angle % 360

    def to_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x + self.native_origin.x

    def to_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return (-1 * y) + self.native_origin.y

    def from_native_angle(self, angle: Union[int, float]) -> Union[int, float]:
        angle = angle % 360
        vp_angle = angle - 270
        if vp_angle < -180:
            vp_angle += 360
        return vp_angle

    def from_native_x(self, x: Union[int, float]) -> Union[int, float]:
        return x - self.native_origin.x

    def from_native_y(self, y: Union[int, float]) -> Union[int, float]:
        return -1 * (y - self.native_origin.y)


LocalCoordinateSystem = Union[
    ToioRelativeCoordinateSystem,
    VisualProgrammingCoordinateSystem,
]
