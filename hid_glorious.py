"""
HID record for the Glorious Modem O mouse.
Maybe for others, but it's the only one I have.

This code is far from being complete, only the set single colour
and set effect is done. Those are the one I personally use.
"""
import copy
from enum import IntEnum


class MouseIds:
    def __init__(self, vid: int, pid: int, usage_page: int, usage_id: int):
        self.vid = vid
        self.pid = pid
        self.usage_page = usage_page
        self.usage_id = usage_id


class GloriousEffect(IntEnum):
    OFF = 0
    GLORIOUS = 1            # Rainbow flow
    SINGLE_COLOUR = 2       # Single colour, no special effect
    BREATHING = 3           # Pulse with colour change
    TAIL = 4                # Front to back with colour change
    SEAMLESS_BREATHING = 5  # Colour rotation
    CONSTANT_GRB = 6        # Not in Model O
    RAVE = 7                # Flashing different colours
    RANDOM = 8              # Not in model O
    WAVE = 9                # Rainbow back to front
    SINGLE_BREATHING = 10   # Pulse single colour


model_O_ids = MouseIds(vid=0x258A, pid=0x0036, usage_page=0xFF00, usage_id=1)


class GloriousModelORecord:
    def __init__(self, bytes_data: bytes):
        self.__raw = bytearray(copy.copy(bytes_data))

    def __str__(self) -> str:
        res = f'Mode({GloriousEffect(self.effect).name})'
        res += f', SingleRGB({self.single_rgb:06X})'
        return res

    @property
    def record(self) -> bytes:
        return bytes(copy.copy(self.__raw))

    @property
    def effect(self):
        return self.__raw[0x35]

    @effect.setter
    def effect(self, effect: GloriousEffect):
        self.__raw[0x35] = effect.value
        self.__mark_changed()

    @property
    def single_rgb(self) -> int:
        # RBG to RGB
        return self.__raw[0x39] << 16 | self.__raw[0x3B] << 8 | self.__raw[0x3A]

    @single_rgb.setter
    def single_rgb(self, rgb: int):
        # RGB to RBG
        self.__raw[0x39:0x3C] = [(rgb >> 16) & 0xFF, rgb & 0xFF, (rgb >> 8) & 0xFF]
        self.__mark_changed()

    def __mark_changed(self) -> None:
        self.__raw[0x03] = 0x7B  # 123 for the write "command". 0 when reading.

