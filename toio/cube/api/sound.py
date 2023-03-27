# -*- coding: utf-8 -*-
# ************************************************************
#
#     sound.py
#
#     Copyright 2022 Sony Interactive Entertainment Inc.
#
# ************************************************************

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Union

from toio.cube.api.base_class import CubeCharacteristic, CubeCommand
from toio.device_interface import CubeInterface, GattReadData
from toio.logger import get_toio_logger
from toio.toio_uuid import TOIO_UUID_SOUND_CTRL
from toio.utility import clip

logger = get_toio_logger(__name__)


class SoundId(IntEnum):
    """
    Sound effect ID

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sound#sound-effect-id
    """

    Enter = 0
    Selected = 1
    Cancel = 2
    Cursor = 3
    MatIn = 4
    MatOut = 5
    Get1 = 6
    Get2 = 7
    Get3 = 8
    Effect1 = 9
    Effect2 = 10


class Note(IntEnum):
    """
    Midi notes

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sound#midi-note-number-and-note-name
    """

    C0 = 0
    CS0 = 1
    D0 = 2
    DS0 = 3
    E0 = 4
    F0 = 5
    FS0 = 6
    G0 = 7
    GS0 = 8
    A0 = 9
    AS0 = 10
    B0 = 11
    C1 = 12
    CS1 = 13
    D1 = 14
    DS1 = 15
    E1 = 16
    F1 = 17
    FS1 = 18
    G1 = 19
    GS1 = 20
    A1 = 21
    AS1 = 22
    B1 = 23
    C2 = 24
    CS2 = 25
    D2 = 26
    DS2 = 27
    E2 = 28
    F2 = 29
    FS2 = 30
    G2 = 31
    GS2 = 32
    A2 = 33
    AS2 = 34
    B2 = 35
    C3 = 36
    CS3 = 37
    D3 = 38
    DS3 = 39
    E3 = 40
    F3 = 41
    FS3 = 42
    G3 = 43
    GS3 = 44
    A3 = 45
    AS3 = 46
    B3 = 47
    C4 = 48
    CS4 = 49
    D4 = 50
    DS4 = 51
    E4 = 52
    F4 = 53
    FS4 = 54
    G4 = 55
    GS4 = 56
    A4 = 57
    AS4 = 58
    B4 = 59
    C5 = 60
    CS5 = 61
    D5 = 62
    DS5 = 63
    E5 = 64
    F5 = 65
    FS5 = 66
    G5 = 67
    GS5 = 68
    A5 = 69
    AS5 = 70
    B5 = 71
    C6 = 72
    CS6 = 73
    D6 = 74
    DS6 = 75
    E6 = 76
    F6 = 77
    FS6 = 78
    G6 = 79
    GS6 = 80
    A6 = 81
    AS6 = 82
    B6 = 83
    C7 = 84
    CS7 = 85
    D7 = 86
    DS7 = 87
    E7 = 88
    F7 = 89
    FS7 = 90
    G7 = 91
    GS7 = 92
    A7 = 93
    AS7 = 94
    B7 = 95
    C8 = 96
    CS8 = 97
    D8 = 98
    DS8 = 99
    E8 = 100
    F8 = 101
    FS8 = 102
    G8 = 103
    GS8 = 104
    A8 = 105
    AS8 = 106
    B8 = 107
    C9 = 108
    CS9 = 109
    D9 = 110
    DS9 = 111
    E9 = 112
    F9 = 113
    FS9 = 114
    G9 = 115
    GS9 = 116
    A9 = 117
    AS9 = 118
    B9 = 119
    C10 = 120
    CS10 = 121
    D10 = 122
    DS10 = 123
    E10 = 124
    F10 = 125
    FS10 = 126
    G10 = 127
    NO_SOUND = 128


@dataclass
class MidiNote:
    """
    Midi note
    """

    duration_ms: int
    """
    | Duration of sounding note:
    |     Any fraction less than 10ms will be truncated.
    |     0 - 9: zero
    |     10 - 2550: duration [ms]
    """
    note: Note
    """
    Midi note
    """
    volume: int
    """
    | Volume:
    |     0: off
    |     1 - 255: max volume
    """

    def flatten(self):
        volume = clip(self.volume, 0, 255)
        duration = clip(int(self.duration_ms / 10), 0, 255)
        return duration, self.note, volume


class PlaySoundEffect(CubeCommand):
    """
    Play sound effect command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sound#playing-sound-effects
    """

    _payload_id = 0x02
    _converter = struct.Struct("<BBB")

    def __init__(self, sound_id: int, volume: int):
        self.sound_id = sound_id
        self.volume = max(min(volume, 255), 0)

    def __bytes__(self) -> bytes:
        return self._converter.pack(self._payload_id, self.sound_id, self.volume)


class PlayMidi(CubeCommand):
    """
    Play midi notes command

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sound#playing-the-midi-note-numbers
    """

    _payload_id = 0x03
    _converter = struct.Struct("<BBB")

    def __init__(self, repeat: int, notes: Union[list[MidiNote], tuple[MidiNote, ...]]):
        self.repeat = repeat
        self.notes = notes

    def __bytes__(self) -> bytes:
        byte_data = self._converter.pack(self._payload_id, self.repeat, len(self.notes))
        for note in self.notes:
            byte_data = byte_data + struct.pack("<BBB", *note.flatten())
        return byte_data


class Stop(CubeCommand):
    """
    Stop sound command
    """

    _payload_id = 0x01

    def __init__(self):
        pass

    def __bytes__(self) -> bytes:
        return bytes(self._payload_id)


class Sound(CubeCharacteristic):
    """
    Sound characteristic

    References:
        https://toio.github.io/toio-spec/en/docs/ble_sound
    """

    @staticmethod
    def is_my_data(_payload: GattReadData) -> None:
        return None

    def __init__(self, interface: CubeInterface):
        self.interface = interface
        super().__init__(interface, TOIO_UUID_SOUND_CTRL)

    async def play_sound_effect(self, sound_id: SoundId, volume: int):
        """
        Send play sound effect command

        Args:
            sound_id (SoundId): Sound ID
            volume (int): Volume
        """
        sound_effect = PlaySoundEffect(sound_id, volume)
        await self._write(bytes(sound_effect))

    async def play_midi(
        self, repeat: int, midi_notes: Union[list[MidiNote], tuple[MidiNote, ...]]
    ):
        """
        Send play midi note command

        Args:
            repeat (int): Number of repetitions (0: Infinite)
            midi_notes (Union[list[MidiNote], tuple[MidiNote, ...]]): List of midi notes
        """
        midi = PlayMidi(repeat, midi_notes)
        await self._write(bytes(midi))

    async def stop(self):
        """
        Send sound stop command
        """
        stop = Stop()
        await self._write(bytes(stop))
