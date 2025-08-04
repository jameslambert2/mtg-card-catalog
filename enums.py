from enum import Enum
Color={
    "COLORLESS":0,
    "VARIABLE":0,
    "BLACK":0x01,
    "WHITE":0x02,
    "GREEN":0x04,
    "BLUE" :0x08,
    "RED"  :0x10,
}

class Type(Enum):
    Artifacts = 1
    Creatures = 2
    Enchantments = 3
    Instants = 4
    Lands = 5
    Planeswalkers = 6
    Sorceries = 7
    Kindreds = 8
    Dungeons = 9
    Battles = 10
    Planes = 11
    Phenomena = 12
    Vanguards = 13
    Schemes = 14
    Conspiracies = 15

class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    MYTHIC = 4
