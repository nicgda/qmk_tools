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
    CONSTANT_RGB = 6        # Six fixed colours
    RAVE = 7                # Flashing different colours
    RANDOM = 8              # Random led colours
    WAVE = 9                # Rainbow back to front
    SINGLE_BREATHING = 10   # Pulse single colour


class EffectDirection(IntEnum):
    FINGERS_TO_PALM = 0
    PALM_TO_FINGERS = 1


model_O_ids = MouseIds(vid=0x258A, pid=0x0036, usage_page=0xFF00, usage_id=1)


class GloriousModelORecord:
    def __init__(self, bytes_data: bytes):
        self.__raw = bytearray(copy.copy(bytes_data))

    def __str__(self) -> str:
        res = 'Glorious Model O configuration:'
        res += f'\n\tMode({GloriousEffect(self.effect).name})'
        res += f'\n\tGlorious({self.glorious_direction.name}, {self.glorious_speed})'
        res += f'\n\tSingle RGB({self.single_rgb:06X}, {self.single_rgb_brightness})'
        res += f'\n\tBreathing({[f"{rgb:06X}" for rgb in self.breath_rgbs]}, {self.breath_speed})'
        res += f'\n\tTail({self.tail_brightness}, {self.tail_speed})'
        res += f'\n\tSeamless Breathing({self.seamless_speed})'
        res += f'\n\tSix RGB({[f"{rgb:06X}" for rgb in self.constant_rgbs]})'
        res += f'\n\tRave({[f"{rgb:06X}" for rgb in self.rave_rgbs]}, {self.rave_brightness}, {self.rave_speed})'
        res += f'\n\tRandom({self.random_speed})'
        res += f'\n\tWave({self.wave_brightness}, {self.wave_speed})'
        res += f'\n\tBreathing mono({self.single_breath_rgb:06X}, {self.single_breath_speed})'
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
    def glorious_direction(self) -> EffectDirection:
        """
        Glorious effect direction of the colour change.
        """
        return EffectDirection(self.__raw[0x37])

    @glorious_direction.setter
    def glorious_direction(self, direction: EffectDirection):
        """
        Glorious effect direction of the colour change.
        """
        self.__raw[0x37] = direction.value
        self.__mark_changed()

    @property
    def glorious_speed(self) -> int:
        """
        Value between 1 and 4.
        """
        return self.__raw[0x36] & 0x0F

    @glorious_speed.setter
    def glorious_speed(self, speed_1_4: int):
        """
        Glorious effect direction of the colour change.
        """
        self.__raw[0x36] = _compact_brightness_speed(4, speed_1_4)
        self.__mark_changed()

    @property
    def single_rgb(self) -> int:
        # RBG to RGB
        return _rbg_to_rgb(self.__raw[0x39:0x3C])

    @single_rgb.setter
    def single_rgb(self, rgb: int):
        # RGB to RBG
        self.__raw[0x39:0x3C] = _rgb_to_rbg(rgb)
        self.__mark_changed()

    @property
    def single_rgb_brightness(self) -> int:
        return self.__raw[0x38] >> 4

    @single_rgb_brightness.setter
    def single_rgb_brightness(self, brightness_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x38] = _compact_brightness_speed(brightness_1_4, 0)
        self.__mark_changed()

    @property
    def breath_speed(self) -> int:
        return self.__raw[0x3C] & 0x0F

    @breath_speed.setter
    def breath_speed(self, speed_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x3C] = _compact_brightness_speed(4, speed_1_4)
        self.__mark_changed()

    @property
    def breath_rgbs(self) -> list[int]:
        """
        Upto seven RGB values for breathing effect
        """
        count = self.__raw[0x3D]
        values = []
        base_addr = 0x3E
        for _ in range(count):
            values.append(_rbg_to_rgb(self.__raw[base_addr:base_addr + 3]))
            base_addr += 3
        return values

    @breath_rgbs.setter
    def breath_rgbs(self, rgbs: list[int] | tuple[int, ...]) -> None:
        """
        Maximum of seven values.
        """
        if 0 < len(rgbs) <= 7:
            self.__raw[0x3D] = len(rgbs)
            base_addr = 0x3E
            for value in rgbs:
                self.__raw[base_addr:(base_addr + 3)] = _rgb_to_rbg(value)
                base_addr += 3
            self.__mark_changed()

    @property
    def tail_brightness(self) -> int:
        return self.__raw[0x53] >> 4

    @tail_brightness.setter
    def tail_brightness(self, brightness_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x53] = _compact_brightness_speed(brightness_1_4, self.tail_speed)
        self.__mark_changed()

    @property
    def tail_speed(self) -> int:
        return self.__raw[0x53] & 0x0F

    @tail_speed.setter
    def tail_speed(self, speed_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x53] = _compact_brightness_speed(self.tail_brightness, speed_1_4)
        self.__mark_changed()

    @property
    def seamless_speed(self) -> int:
        return self.__raw[0x54] & 0x0F

    @seamless_speed.setter
    def seamless_speed(self, speed_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x54] = _compact_brightness_speed(4, speed_1_4)
        self.__mark_changed()

    @property
    def constant_rgbs(self) -> list[int]:
        # RBG to RGB
        values = []
        base_addr = 0x56
        for _ in range(6):
            values.append(_rbg_to_rgb(self.__raw[base_addr:base_addr + 3]))
            base_addr += 3
        return values

    @constant_rgbs.setter
    def constant_rgbs(self, six_rgbs: list[int] | tuple[int, int, int, int, int, int]) -> None:
        """
        The brightness and speed don't have any effects.
        """
        if len(six_rgbs) == 6:
            self.__raw[0x55] = 0  # Original value from the mouse
            base_addr = 0x56
            for value in six_rgbs:
                self.__raw[base_addr:(base_addr + 3)] = _rgb_to_rbg(value)
                base_addr += 3
            self.__mark_changed()

    @property
    def rave_brightness(self) -> int:
        return self.__raw[0x74] >> 4

    @rave_brightness.setter
    def rave_brightness(self, brightness_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x74] = _compact_brightness_speed(brightness_1_4, self.rave_speed)
        self.__mark_changed()

    @property
    def rave_speed(self) -> int:
        return self.__raw[0x74] & 0x0F

    @rave_speed.setter
    def rave_speed(self, speed_1_3: int):
        """
        Value between 1 and 3.
        """
        self.__raw[0x74] = _compact_brightness_speed(self.rave_brightness, speed_1_3, max_speed=3)
        self.__mark_changed()

    @property
    def rave_rgbs(self) -> list[int]:
        """
        Two RGB values
        """
        return [
            _rbg_to_rgb(self.__raw[0x75:0x78]),
            _rbg_to_rgb(self.__raw[0x78:0x7B])
        ]

    @rave_rgbs.setter
    def rave_rgbs(self, rgbs: list[int] | tuple[int, int]) -> None:
        """
        Maximum of seven values.
        """
        if len(rgbs) == 2:
            base_addr = 0x75
            for value in rgbs:
                self.__raw[base_addr:(base_addr + 3)] = _rgb_to_rbg(value)
                base_addr += 3
            self.__mark_changed()

    @property
    def random_speed(self) -> int:
        return self.__raw[0x7B] & 0x0F

    @random_speed.setter
    def random_speed(self, speed_1_3: int):
        """
        Value between 1 and 3.
        """
        self.__raw[0x7B] = _compact_brightness_speed(0, speed_1_3, max_speed=3)
        self.__mark_changed()

    @property
    def wave_brightness(self) -> int:
        return self.__raw[0x7C] >> 4

    @wave_brightness.setter
    def wave_brightness(self, brightness_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x7C] = _compact_brightness_speed(brightness_1_4, self.wave_speed)
        self.__mark_changed()

    @property
    def wave_speed(self) -> int:
        return self.__raw[0x7C] & 0x0F

    @wave_speed.setter
    def wave_speed(self, speed_1_3: int):
        """
        Value between 1 and 3.
        """
        self.__raw[0x74C] = _compact_brightness_speed(self.wave_brightness, speed_1_3, max_speed=3)
        self.__mark_changed()

    @property
    def single_breath_speed(self) -> int:
        return self.__raw[0x7D] & 0x0F

    @single_breath_speed.setter
    def single_breath_speed(self, speed_1_4: int):
        """
        Value between 1 and 4.
        """
        self.__raw[0x7D] = _compact_brightness_speed(0, speed_1_4)
        self.__mark_changed()

    @property
    def single_breath_rgb(self) -> int:
        # RBG to RGB
        return _rbg_to_rgb(self.__raw[0x7E:0x81])

    @single_breath_rgb.setter
    def single_breath_rgb(self, rgb: int):
        # RGB to RBG
        self.__raw[0x7E:0x81] = _rgb_to_rbg(rgb)
        self.__mark_changed()

    def __mark_changed(self) -> None:
        self.__raw[0x03] = 0x7B  # 123 for the write "command". 0 when reading.


def _rgb_to_rbg(rgb: int) -> list[int]:
    return [(rgb >> 16) & 0xFF, rgb & 0xFF, (rgb >> 8) & 0xFF]


def _rbg_to_rgb(rbg_list: bytearray) -> int:
    return rbg_list[0] << 16 | rbg_list[2] << 8 | rbg_list[1]


def _limit_1_max(value: int, max_value: int) -> int:
    if max_value > 15:
        max_value = 15  # Safety
    if value < 1:
        return 1
    elif value > max_value:
        return max_value
    return value


def _compact_brightness_speed(brightness_1_4: int, speed_1_4: int, max_brightness: int = 4, max_speed: int = 4) -> int:
    return _limit_1_max(brightness_1_4, max_brightness) << 4 | _limit_1_max(speed_1_4, max_speed)
