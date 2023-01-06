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




# Source: https://git.sammserver.com/sammko/gloryctl/src/master
#
# Header (00-0C)
#   04
#   11
#   00
#   00 - Read:00, Write:7B (dec 123)
#   00 00
#   00
#   00 64
#   06
#   04
#   34
#   f0
#
# DPI profiles (0D-34)
#   03 07 0f 1f 31 63 00 00 00 00 00 00 00 00 00 00 - 16 bytes
#
#   ff ff 00 - 8 profiles RGB color
#   00 00 ff
#   ff 00 00
#   00 ff 00
#   ff 00 ff
#   ff ff ff
#   00 00 00
#   00 00 00
#
# RGB effects (35-80)
#   BS byte: Brightness (4 upper bits) and Speed (4 lower bits)
#
# -- Current effect (35) --
#   01
# -- Glorious effect config (36-37) --
#   41 - BS
#   00 - direction (bool)
# -- Single colour effect (38-3B) --
#   40 - BS
#   ff 00 00 - RBG (Red, Blue, Green)
# -- Breathing effect (3C-52) --
#   42  - BS
#   07  - Number of colours used (out of 7)
#   ff 00 00 - Colors in RBG (Red, Blue, Green)
#   00 ff 00
#   00 00 ff
#   00 ff ff
#   ff ff 00
#   ff 00 ff
#   ff ff ff
# -- Tail effect (53) --
#   42 - BS
# -- Seamless breathing effect (54) --
#   42 -BS
# -- Constant RGB effect (55-67) --
#   00 - BS
#   ff 00 00 - Six RBG for 6 leds on each sides
#   00 ff 00
#   00 00 ff
#   ff ff 00
#   00 ff ff
#   ff ff ff
# -- Unknown (68-73) --
#   fa 00 ff ff 00 00 ff 00 00 ff 00 00
# -- Rave effect (74-7A) --
#   42 - BS
#   ff 00 00 - Two RBG colors
#   00 ff 00
# -- Random effects (7B) --
#   02 - BS
# -- Wave effect (7C) --
#   42 - BS
# -- Single colour breathing effect (7D-80) --
#   02 - BS
#   ff 00 00 - RBG
#
