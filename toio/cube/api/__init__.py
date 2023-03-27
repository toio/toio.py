# -*- coding: utf-8 -*-
# ************************************************************
#
#     toio/cube/api/__init__.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

from ...device_interface import CubeInterface
from .battery import Battery
from .button import Button
from .configuration import Configuration
from .id_information import IdInformation
from .indicator import Indicator
from .motor import Motor
from .sensor import Sensor
from .sound import Sound

API_VERSION = "2.3.0"


class ToioCoreCubeLowLevelAPI(object):
    """
    Control APIs
    This class has control APIs for each characteristic.

    Attributes:
        version (str): Version of supported API
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

    def __init__(self, interface: CubeInterface):
        self.version = API_VERSION
        self.battery = Battery(interface)
        self.button = Button(interface)
        self.configuration = Configuration(interface)
        self.id_information = IdInformation(interface)
        self.indicator = Indicator(interface)
        self.motor = Motor(interface)
        self.sensor = Sensor(interface)
        self.sound = Sound(interface)
