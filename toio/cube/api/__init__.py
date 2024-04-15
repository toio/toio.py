# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/cube/api/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from __future__ import annotations

from typing_extensions import TypeAlias, Union

from ...device_interface import CubeInterface
from ..notification_handler_info import NotificationReceivedDevice
from .battery import Battery
from .button import Button
from .configuration import Configuration
from .id_information import IdInformation
from .indicator import Indicator
from .motor import Motor
from .sensor import Sensor
from .sound import Sound

API_VERSION = "2.4.0"

CubeApi: TypeAlias = Union[
    Battery, Button, Configuration, IdInformation, Indicator, Motor, Sensor, Sound
]


class ToioCoreCubeLowLevelAPI:
    """
    Control APIs
    This class has control APIs for each characteristic.

    Attributes:
        battery (api.Battery): Interface to `battery characteristic <https://toio.github.io/toio-spec/en/docs/ble_battery>`_
        button (api.Button): Interface to `button characteristic <https://toio.github.io/toio-spec/en/docs/ble_button>`_
        configuration (api.Configuration): Interface to `configuration characteristic <https://toio.github.io/toio-spec/en/docs/ble_configuration>`_
        id_information (api.IdInformation): Interface to `id information characteristic <https://toio.github.io/toio-spec/en/docs/ble_id>`_
        indicator (api.IdInformation): Interface to `indicator characteristic <https://toio.github.io/toio-spec/en/docs/ble_light>`_
        motor (api.Motor): Interface to `motor characteristic <https://toio.github.io/toio-spec/en/docs/ble_motor>`_
        sensor (api.Sensor): Interface to sensor characteristic (
         `Motion <https://toio.github.io/toio-spec/en/docs/ble_sensor>`_
         `Posture <https://toio.github.io/toio-spec/en/docs/ble_high_precision_tilt_sensor>`_
         `Magnet <https://toio.github.io/toio-spec/en/docs/ble_magnetic_sensor>`_
         )
        sound (api.Sound): Interface to `sound characteristic <https://toio.github.io/toio-spec/en/docs/ble_sound>`_
    """

    def __init__(
        self, interface: CubeInterface, root_device: NotificationReceivedDevice
    ):
        self._version = API_VERSION
        self.battery = Battery(interface, root_device)
        self.button = Button(interface, root_device)
        self.configuration = Configuration(interface, root_device)
        self.id_information = IdInformation(interface, root_device)
        self.indicator = Indicator(interface, root_device)
        self.motor = Motor(interface, root_device)
        self.sensor = Sensor(interface, root_device)
        self.sound = Sound(interface, root_device)

    @property
    def version(self) -> str:
        DeprecationWarning(
            "use ToioCoreCube.SUPPORTED_MAJOR_VERSION and ToioCoreCube.SUPPORTED_MINOR_VERSION"
        )
        return self._version
