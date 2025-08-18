"""
database_search.py

Created By: James Lambert
Last Updated: 11 Aug 2025

This file assist with the seaching of the database of cards.
It generates the SQL Command and runs it, returning the values from the results.
"""

import sqlite3
import enum
from typing import List
import os

from .update_db.enums import Rarity, Color

script_dir = os.path.dirname(__file__)
REL_PATH = "card_db.db"

DB_FILE = os.path.abspath(os.path.join(script_dir, REL_PATH))


class DbOrder(enum.Enum):
    """
    Indexes for the results list
    """

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


class DbCard:
    """
    DbCard Object
    """

    def __init__(self, fetch_results):
        """initialization function for DbCard
        
        Initialization function for the DbCard Object. Taking the data
        from fetch_results and saving them to specific data inside the DbCard

        Args:
            fetch_results: List - results from cursor.fetchone
                (or each item from cursor.fetchall)
        """
        self.card_id = fetch_results[DbOrder.ID.value]
        self.set = fetch_results[DbOrder.SET.value]
        self.title = fetch_results[DbOrder.TITLE.value]
        self.img_url = fetch_results[DbOrder.IMG_URL.value]
        self.card_type = fetch_results[DbOrder.TYPE.value]
        self.subtype = fetch_results[DbOrder.SUBTYPE.value]
        quote = fetch_results[DbOrder.QUOTE.value]
        rarity = Rarity(fetch_results[DbOrder.RARITY.value])
        color = fetch_results[DbOrder.COLOR.value]
        cost = fetch_results[DbOrder.COST.value]
        abilities = fetch_results[DbOrder.ABILITIES.value]
        self.details = (quote, rarity, color, cost, abilities)

    def show_details(self):
        """
        get details for the card.
        
        detail order: Quote, Rarity, Color, Cost, Abilities
        """
        return self.details

    def __str__(self):
        """
        String representation of the DbCard Object
        """
        return f"ID: {self.card_id:<6}\tSet:{self.set:<6}\tName: {self.title}"


class SearchResults:
    """
    SearchResults uses a provided Cursor to generate a query lookup 
    for the results requested
    """

    def __init__(self, cursor: sqlite3.Cursor):
        """
        Initialization function for SearchResults Object

        Args:
            cursor: sqlite3.Cursor - the connection to the database file
        """
        self.cursor = cursor
        self.last_result = []

    def get_set_by_title(self, title):
        """
        Build a search query for sets using the set's title or shortened name.

        Args:
            title: str
        """
        fmt = "SELECT shortened FROM sets WHERE shortened LIKE '%{0}%' OR title LIKE '%{0}%'"
        self.cursor.execute(fmt.format(title))
        set_list = self.cursor.fetchall()
        return set_list

    def get_card_by_id(self, card_id) -> DbCard:
        """
        Build a search query for cards using the card's id.

        Args:
            card_id: int
        """
        fmt = "SELECT * FROM cards WHERE id = {0}"
        self.cursor.execute(fmt.format(card_id))
        fetch_results = self.cursor.fetchone()
        self.last_result.clear()
        self.last_result.append(fetch_results)
        card = DbCard(fetch_results)
        return card

    def search_cards_by_title(self, title) -> List[DbCard]:
        """
        Build a search query for cards using the card's title.

        Args:
            title: str
        """
        fmt = "SELECT * FROM cards WHERE title LIKE '%{0}%'"
        self.cursor.execute(fmt.format(title))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DbCard(each))
        self.last_result = cards
        return cards

    def search_cards_by_set(self, set_shortened) -> List[DbCard]:
        """
        Build a search query for cards using the Shortened Set name.

        Args:
            card_set: str
        """
        fmt = "SELECT * FROM cards c WHERE set_shortened LIKE '%{0}%'"
        self.cursor.execute(fmt.format(set_shortened))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DbCard(each))
        return cards

    def get_all_cards(self) -> List[DbCard]:
        """
        Build a search query for getting all cards
        """
        fmt = "SELECT * FROM cards"
        self.cursor.execute(fmt)
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DbCard(each))
        return cards

    def search_results_by_color(self, color: str) -> List[DbCard]:
        """
        Build a search query for cards using card color.

        Args:
            color: str (Options: "RED","BLUE","GREEN","WHITE","BLACK","COLORLESS")
        """
        try:
            Color[color.upper()]
        except KeyError:
            return []
        fmt = "SELECT * FROM cards c WHERE c.color & {0} != 0"
        self.cursor.execute(fmt.format(Color[color.upper()]))
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results
        cards = []
        for each in fetch_results:
            cards.append(DbCard(each))
        return cards

    def multi_command_building(self, **kwargs):
        """
        Build a flexible search query for cards using keyword arguments.

        Supported kwargs:
            title (str)
            set_shortened (str)
            color (str) - matches keys in Color enum
            rarity (Rarity)
            card_type (str)
            subtype (str)
        """
        query = "SELECT * FROM cards WHERE 1=1"
        params = []
        subtype = kwargs.get("subtype")
        card_type = kwargs.get("card_type")
        rarity = kwargs.get("rarity")
        set_shortened = kwargs.get("set_shortened")
        title = kwargs.get("title")
        color = kwargs.get("color")
        # Subtype
        if subtype:
            query += " AND subtype LIKE ?"
            params.append(f"%{subtype}%")

        # Card type
        if card_type:
            query += " AND type LIKE ?"
            params.append(f"%{card_type}%")

        # Rarity
        if rarity and rarity.value != 0:
            query += " AND rarity = ?"
            params.append(rarity.value)

        # Color
        if color:
            if Color[color] == 0:  # colorless
                query += " AND color = ?"
            else:
                query += " AND color & ? != 0"
            params.append(Color[color])

        # Set search (matches multiple variations)
        if set_shortened:
            tmp = self.get_set_by_title(set_shortened)
            if tmp:
                query += " AND (set_shortened LIKE ?"
                params.append(f"%{tmp[0]}%")
                for each in tmp[0:]:
                    query += " OR set_shortened LIKE ?"
                    params.append(f"%{each[0]}%")
                query += ")"

        # Title
        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")

        # Execute
        self.cursor.execute(query, params)
        fetch_results = self.cursor.fetchall()
        self.last_result = fetch_results

        return [DbCard(each) for each in fetch_results]
