from enum import Enum

Color = {
    "COLORLESS": 0,
    "VARIABLE": 0,
    "BLACK": 0x01,
    "WHITE": 0x02,
    "GREEN": 0x04,
    "BLUE": 0x08,
    "RED": 0x10,
}


class Rarity(Enum):
    UNKNOWN = 0
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    MYTHIC_RARE = 4
