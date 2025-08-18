"""
lookup.py

Lookup the details of the MTG cards and sets for the catalog (database)
for putting the information into the database

Written by: James Lambert
Last Updated: 18 Aug 2025
"""
import json
import sqlite3
from enum import Enum

import requests
from bs4 import BeautifulSoup

from src.update_db.sets import MTGSet, sets
from src.update_db.card import Card
from src.database_search import DB_FILE


BASE_URL = "https://aetherhub.com"
SET_URL = BASE_URL + "/Card/Set"

class Details(Enum):
    """
    enum for detail indexes
    """
    QUOTE = 0
    RARITY = 1
    COLOR = 2
    COST = 3
    ABILITIES = 4


def gather_cards(conn, cursor):
    """
    Gathers cards by set and puts them into the database of cards
    if the set is not already in there.
    Args:
        conn(sqlite3.Connection): Connection to the database
        cursor (sqlite3.Connection.Cursor): Cursor for lookups and
            executing sql commands
    """
    for card_set in sets:
        temp = MTGSet(card_set)
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM sets WHERE shortened = ?)", (temp.shortened,)
        )
        if cursor.fetchone()[0]:
            continue
        print(temp.title)
        req = requests.get(temp.url, timeout=15)
        soup = BeautifulSoup(req.content, "html.parser")
        cards = soup.find("div", id="cards")
        card_list = cards.find_all("a", class_="item ae-card-link cardLink")
        set_shortened = insert_set(cursor, temp)
        for card in card_list:
            title = card.find("div", class_="item-hidden-text").contents[0]
            url = BASE_URL + card.get("href")
            page = requests.get(url, timeout=15)
            try:
                temp_card = Card(title, temp, page)
                insert_card(cursor, temp_card, set_shortened)
            except Warning:
                print(f"Invalid Card : {title}")
        conn.commit()


def insert_set(cursor, card_set: MTGSet):
    """
    Insert a set into the database of sets

    Args:
        cursor (sqlite3.Connection.Cursor): Cursor for lookups and
            executing sql commands
        card_set (MTGSet): Set object to get the information from to
            add to the database
    """
    cursor.execute(
        """
        INSERT OR IGNORE INTO sets (shortened, title, release_date, url)
        VALUES (?, ?, ?, ?)
    """,
        (card_set.shortened, card_set.title, card_set.release_date, card_set.url),
    )
    return card_set.shortened


def insert_card(cursor, card: Card, set_shortened: str):
    """
    Insert a card into the database of cards

    Args:
        cursor (sqlite3.Connection.Cursor): Cursor for lookups and
            executing sql commands
        card (Card): Card object to get the information from to
            add to the database
        set_shortened (str): The short hand label of the set that
            the card is from.
    """
    cursor.execute(
        """
        INSERT INTO cards (
            set_shortened, title, img_url, type, subtype, quote,
            rarity, color, mana_cost, abilities
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            set_shortened,
            card.title,
            card.img_url,
            card.type,
            card.subtype,
            card.details[Details.QUOTE.value],
            card.details[Details.RARITY.value].value,
            card.details[Details.COLOR.value],
            json.dumps(card.details[Details.COST.value]),
            json.dumps(card.details[Details.ABILITIES.value]),
        ),
    )


if __name__ == "__main__":
    # for each in all_cards:
    #     print(each.display())
    connection = sqlite3.connect(DB_FILE)
    cursor_use = connection.cursor()
    cursor_use.execute(
        """CREATE TABLE IF NOT EXISTS sets (
    shortened TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    release_date TEXT,
    url TEXT
    );"""
    )

    cursor_use.execute(
        """CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_shortened TEXT NOT NULL,
    title TEXT,
    img_url TEXT,
    type TEXT,
    subtype TEXT,
    quote TEXT,
    rarity INTEGER,
    color INTEGER,
    mana_cost TEXT,
    abilities TEXT,
    FOREIGN KEY(set_shortened) REFERENCES sets(shortened) ON DELETE CASCADE
    );"""
    )

    gather_cards(connection, cursor_use)  # put into database file you want
    connection.close()
