# mtg-card-catalog
## Card Data
 
- Title         str
- Color         int
    - BLACK 0x01
    - WHITE 0x02
    - GREEN 0x04
    - BLUE  0x08
    - RED   0x10
- Mana Cost (dict with color as key, count as value)
- Type (Artifact/Creature/Enchatment etc.) (Enum)

    1. Artifacts 
    2. Creatures
    3. Enchantments
    4. Instants
    5. Lands
    6. Planeswalkers
    7. Sorceries
    8. Kindreds
    9. Dungeons
    10. Battles
    11. Planes
    12. Phenomena
    13. Vanguards
    14. Schemes
    15. Conspiracies

- Subtype       (str)
- Power:        (int)
- Toughness:    (int)
- Abilities:    (list[str])
- Description:  (str)
- Quote         (str)
- Rarity        (Enum)
    - COMMON
    - UNCOMMON
    - RARE
    - MYTHIC
- Foil          (bool)
- Set           (str) (or Enum/Dictionary/List of sets)
- Border Color (Default Black, older White, Unsets Silver)

- Price (Lookup?)
- Card Art?
- Display a card view?

C++ or Python?