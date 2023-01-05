import copy
from enum import IntEnum


class MouseIds:
    def __init__(self, vid:int, pid:int, usage_page:int, usage_id:int):
        self.vid = vid
        self.pid = pid
        self.usage_page = usage_page
        self.usage_id = usage_id


class GloriousEffect(IntEnum):
    OFF = 0
    GLORIOUS = 1  # Rainbow flow
    SINGLE_COLOUR = 2  # Single colour, no special effect
    BREATHING = 3  # Pulse with colour change
    TAIL = 4  # Front to back with colour change
    SEAMLESS_BREATHING = 5  # Colour rotation
    CONSTANT_GRB = 6  # Not in Model O
    RAVE = 7  # Flashing different colours
    RANDOM = 8   # Not in model O
    WAVE = 9  # Rainbow back to front
    SINGLE_BREATHING = 10  # Pulse single colour


model_O_ids = MouseIds(vid=0x258A, pid=0x0036, usage_page=0xFF00, usage_id=1)


class GloriousModelORecord:
    def __init__(self, bytes_data: bytes):
        self.__raw = bytearray(copy.copy(bytes_data))

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

    def __mark_changed(self) -> None:
        self.__raw[0x03] = 0x7B  # 123 for the write "command". 0 when reading.

    # def rgb(self) -> Tuple[int, int, int]:
    #     return raw.


