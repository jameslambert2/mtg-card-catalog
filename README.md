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
- Type (Artifact/Creature/Enchatment etc.) (str)

- Subtype       (str)
- Abilities:    (list[str])
- Description:  (str)
- Quote         (str)
- Rarity        (Enum)
    - COMMON
    - UNCOMMON
    - RARE
    - MYTHIC
- Set           (str) (or Enum/Dictionary/List of sets)

- Card Art
- Display a card view

- Price (Lookup?) Not implemented yet

Python Requirements
For lookup:
    pip install bs4 requests 
For application:
    pip install Pillow