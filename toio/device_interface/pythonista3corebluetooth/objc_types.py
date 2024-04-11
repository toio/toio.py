# -*- coding: utf-8 -*-
# ************************************************************
#
#     objc_types.py
#
#     Copyright 2024 Sony Interactive Entertainment Inc.
#
# ************************************************************

import ctypes

from objc_util import ObjCClass, ObjCInstance, c
from typing_extensions import TypeAlias

CBCentralManager = ObjCClass("CBCentralManager")
CBCentralManagerType: TypeAlias = ObjCClass
CBCharacteristic = ObjCClass("CBCharacteristic")
CBCharacteristicType: TypeAlias = ObjCClass
CBDescriptor = ObjCClass("CBDescriptor")
CBDescriptorType: TypeAlias = ObjCClass
CBPeripheral = ObjCClass("CBPeripheral")
CBPeripheralType: TypeAlias = ObjCClass
CBPeripheralManager = ObjCClass("CBPeripheralManager")
CBPeripheralManagerType: TypeAlias = ObjCClass
CBService = ObjCClass("CBService")
CBServiceType: TypeAlias = ObjCClass
CBUUID = ObjCClass("CBUUID")
CBUUIDType: TypeAlias = ObjCClass
NSArrayType: TypeAlias = ObjCClass
NSError = ObjCClass("NSError")
NSErrorType: TypeAlias = ObjCClass

CBManagerStateUnknown = 0
CBManagerStateResetting = 1
CBManagerStateUnsupported = 2
CBManagerStateUnauthorized = 3
CBManagerStatePoweredOff = 4
CBManagerStatePoweredOn = 5

CBCharacteristicWriteWithResponse = 0
CBCharacteristicWriteWithoutResponse = 1

CBPeripheralStateDisconnected = 0
CBPeripheralStateConnecting = 1
CBPeripheralStateConnected = 2
CBPeripheralStateDisconnecting = 3

DISPATCH_QUEUE_SERIAL = None

NSKeyValueObservingOptionNew = 0x01

# https://forum.omz-software.com/topic/6077/help-finding-the-value-of-an-objc-string-constant
NSKeyValueChangeNewKey = ObjCInstance(
    ctypes.c_void_p.in_dll(c, "NSKeyValueChangeNewKey")
)


def dispatch_queue_create(_name, attr):
    _func = c.dispatch_queue_create
    _func.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
    _func.restype = ctypes.c_void_p
    name = _name.encode("ascii")
    return ObjCInstance(_func(name, attr))
