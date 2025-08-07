import sqlite3
import enum
from enums import Rarity, Color
from typing import List
import json


class DB_Order(enum.Enum):
    ID = 0
    SET = 1
    TITLE = 2
    IMG_URL = 3
    TYPE = 4
    SUBTYPE = 5
    QUOTE = 6
    RARITY = 7
    COLOR = 8
    COST = 9
    ABILITIES = 10


class DB_Card:
    def __init__(self, fetch_results):
        self.id = fetch_results[DB_Order.ID.value]
        self.set = fetch_results[DB_Order.SET.value]
        self.title = fetch_results[DB_Order.TITLE.value]
        self.img_url = fetch_results[DB_Order.IMG_URL.value]
        self.type = fetch_results[DB_Order.TYPE.value]
        self.subtype = fetch_results[DB_Order.SUBTYPE.value]
        self.quote = fetch_results[DB_Order.QUOTE.value]
        self.rarity = Rarity(fetch_results[DB_Order.RARITY.value])
        self.color = fetch_results[DB_Order.COLOR.value]
        self.cost = fetch_results[DB_Order.COST.value]
        self.abilities = fetch_results[DB_Order.ABILITIES.value]

    def __str__(self):
        pass


class Search_Results:
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor
        self.last_result = []

    def get_card_by_id(self, id) -> DB_Card:
        fmt = "SELECT * FROM cards WHERE id = {0}"
        self.cursor.execute(fmt.format(id))
        fetch_results = self.cursor.fetchone()
        self.last_result.clear()
        self.last_result.append(fetch_results)
        card = DB_Card(fetch_results)
        return card

    def search_cards_by_title(self, title) -> List[DB_Card]:
        fmt = "SELECT * FROM cards WHERE title LIKE '%{0}%'"
        self.cursor.execute(fmt.format(title))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DB_Card(each))
        self.last_result = cards
        return cards

    def search_cards_by_set(self, set_shortened) -> List[DB_Card]:
        fmt = "SELECT * FROM cards c WHERE set_shortened LIKE '%{0}%'"
        self.cursor.execute(fmt.format(set_shortened))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DB_Card(each))
        return cards

    def get_all_cards(self) -> List[DB_Card]:
        fmt = "SELECT * FROM cards"
        self.cursor.execute(fmt)
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DB_Card(each))
        return cards

    def search_results_by_color(self, color: str) -> List[DB_Card]:
        if color.upper() not in Color.keys():
            return []
        fmt = "SELECT * FROM cards c WHERE c.color & {0} != 0"
        self.cursor.execute(fmt.format(Color[color.upper()]))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DB_Card(each))
        return cards


# class DB_Set:
#     def __init__(self, cursor: sqlite3.Cursor):
#         self.cursor = cursor


if __name__ == "__main__":
    conn = sqlite3.connect('card_db.db')
    cursor = conn.cursor()
    sr = Search_Results(cursor)

    cards = sr.get_all_cards()
    for each in cards:
        print(f"Set:{each.set}\tID:{each.id:>6}\t Title: ", each.title)

    conn.close()
