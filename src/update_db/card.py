"""
card.py

Details of the MTG cards for the catalog (database) for more lookup viability

Written by: James Lambert
Last Updated: 18 Aug 2025
"""
import requests
from bs4 import BeautifulSoup

from src.update_db.enums import Rarity, Color
from src.update_db.sets import MTGSet

MAX_COLORLESS = 20  # Estimate

name_to_rarity = {
    "COMMON": Rarity.COMMON,
    "UNCOMMON": Rarity.UNCOMMON,
    "RARE": Rarity.RARE,
    "MYTHIC_RARE": Rarity.MYTHIC_RARE,
}

color_dict = {
    "ms-r": "RED",
    "ms-u": "BLUE",
    "ms-w": "WHITE",
    "ms-b": "BLACK",
    "ms-g": "GREEN",
    "ms-x": "VARIABLE",
}
for x in range(MAX_COLORLESS):
    color_dict[f"ms-{x}"] = "COLORLESS"


class Card:
    """
    Card details for updating the Database.

    Args:
        title (str): Name of the card
        card_set (MTGSet): Set the card is a part of
        page (requests.Response): The request.get() response containing
            the page details
    """
    def __init__(self, title: str, card_set: MTGSet, page: requests.Response):
        self.title = title
        self.soup = BeautifulSoup(page.content, "html.parser")
        temp = self.soup.find("div", id="cardInfo")
        if not temp:
            raise Warning
        self.img_url = temp.find("img")["src"]
        card_details = temp.find("div", class_="col-sm-12 col-md-6 mt-3 mt-md-0")
        self.set = card_set
        self.get_details(card_details)


    def get_details(self, card_details: BeautifulSoup._AtMostOneElement):
        """
        Get the details of this card, including quote, rarity, color, mana
            cost, and abilities. This is not returned, it is updated in 
            self.details

        Args:
            card_details (BeautifulSoup._AtMostOneElement): 
                Result from BeautifulSoup.find() containing card information
        
        """
        cost, mana_cost = self.get_mana_cost(card_details)
        color = 0
        if len(cost) != 0:
            for colorcosts in mana_cost:
                color += Color[colorcosts]

        paragraphs = card_details.find_all("p")
        temp = paragraphs[0].contents[0].split("—")
        self.type = temp[0]
        if len(temp) > 1:
            self.subtype = temp[1]
        else:
            self.subtype = ""

        quote = str(paragraphs[-2].contents[0])
        quote = quote.replace("<i>", "")
        quote = quote.replace("</i>", "")
        abilities = "".join(map(str, paragraphs[1].contents)).split("<br/>")
        # cleanup to show ability mana costs
        for idx, each in enumerate(abilities):
            abilities[idx] = each.replace('<i class="ms ms-', "").replace(
                'ms-cost ms-shadow"></i>', ""
            )
        temp = card_details.find("small").contents[-1]
        temp = temp.strip()
        temp = temp.upper()
        rarity = name_to_rarity.get(temp)
        if not rarity:
            rarity = Rarity.UNKNOWN
        self.details = (quote, rarity, color, mana_cost, abilities)

    def get_mana_cost(self, card_details: BeautifulSoup._AtMostOneElement):
        """
        Get the mana cost of this card

        Args:
            card_details (BeautifulSoup._AtMostOneElement): 
                Result from BeautifulSoup.find() containing the card information
        
        Returns:
            (cost, mana_cost): Tuple(int, dict)
        """
        temp = card_details.find("span", class_="pull-right")
        cost = temp.find_all("i")
        mana_cost = {}
        for item in cost:
            temp = item.get("class")[1]
            try:
                cost_color = color_dict[temp]
            except KeyError:
                break
            if cost_color == "COLORLESS":
                mana_cost[cost_color] = int(temp[3:])
            try:
                mana_cost[cost_color] += 1
            except KeyError:
                mana_cost[cost_color] = 1
        return cost, mana_cost



    def display(self):
        """
        A print display for the card title and set its associated with
        """
        return f"\n\t{self.title} --> {self.set}"

    def __str__(self):
        return f"\n\t{self.title} --> {self.set}"


if __name__ == "__main__":
    pass
