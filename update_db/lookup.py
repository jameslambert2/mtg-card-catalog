from sets import MTG_Set, sets
from card import Card
import json
import sqlite3
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://aetherhub.com"
SET_URL = BASE_URL + "/Card/Set"


def gather_cards(conn, cursor):
    i = 0
    for card_set in sets:
        temp = MTG_Set(card_set)
        cursor.execute(
            f"SELECT EXISTS(SELECT 1 FROM sets WHERE shortened = ?)", (temp.shortened,)
        )
        exists = cursor.fetchone()[0]
        if exists:
            continue
        print(temp.title)
        req = requests.get(temp.url)
        soup = BeautifulSoup(req.content, "html.parser")
        cards = soup.find("div", id="cards")
        card_list = cards.find_all("a", class_="item ae-card-link cardLink")
        set_shortened = insert_set(cursor, temp)
        for card in card_list:
            title = card.find("div", class_="item-hidden-text").contents[0]
            url = BASE_URL + card.get("href")
            page = requests.get(url)
            try:
                temp_card = Card(title, temp, page)
                insert_card(cursor, temp_card, set_shortened)
            except Warning:
                print(f"Invalid Card : {title}")
        conn.commit()


def insert_set(cursor, card_set: MTG_Set):
    cursor.execute(
        """
        INSERT OR IGNORE INTO sets (shortened, title, release_date, url)
        VALUES (?, ?, ?, ?)
    """,
        (card_set.shortened, card_set.title, card_set.release_date, card_set.url),
    )
    return card_set.shortened


def insert_card(cursor, card: Card, set_shortened: str):
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
            card.quote,
            card.rarity.value,
            card.color,
            json.dumps(card.mana_cost),
            json.dumps(card.abilities),
        ),
    )


if __name__ == "__main__":
    # for each in all_cards:
    #     print(each.display())
    conn = sqlite3.connect("card_db.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS sets (
    shortened TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    release_date TEXT,
    url TEXT
    );"""
    )

    cursor.execute(
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

    gather_cards(conn, cursor)  # put into database file you want
    conn.close()
