from enums import Rarity, Color
import requests
from bs4 import BeautifulSoup
from sets import MTG_Set

MAX_COLORLESS = 20  # Estimate

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
    def __init__(self, title: str, set: MTG_Set, page: requests.Response):
        self.title = title
        self.soup = BeautifulSoup(page.content, "html.parser")
        temp = self.soup.find("div", id="cardInfo")
        if not temp:
            raise Warning
        self.img_url = temp.find("img")["src"]
        card_details = temp.find("div", class_="col-sm-12 col-md-6 mt-3 mt-md-0")
        temp_colors = card_details.find("span", class_="pull-right")
        cost = temp_colors.find_all("i")
        self.mana_cost = dict()
        for item in cost:
            temp2 = item.get("class")[1]
            if temp2 in color_dict.keys():
                cost_color = color_dict[temp2]
            else:
                break
            if cost_color == "COLORLESS":
                self.mana_cost[cost_color] = int(temp2[3:])
            elif cost_color in self.mana_cost.keys():
                self.mana_cost[cost_color] += 1
            else:
                self.mana_cost[cost_color] = 1
        self.color = 0
        if len(cost) != 0:
            for colorcosts in self.mana_cost.keys():
                self.color += Color[colorcosts]

        paragraphs = card_details.find_all("p")
        tmp = paragraphs[0].contents[0].split("—")
        self.type = tmp[0]
        if len(tmp) > 1:
            self.subtype = tmp[1]
        else:
            self.subtype = ""

        self.quote = str(paragraphs[-2].contents[0])
        self.quote = self.quote.replace("<i>", "")
        self.quote = self.quote.replace("</i>", "")
        self.set = set

        self.abilities = "".join(map(str, paragraphs[1].contents)).split("<br/>")
        # cleanup to show ability mana costs
        for idx, each in enumerate(self.abilities):
            self.abilities[idx] = each.replace('<i class="ms ms-', "").replace(
                'ms-cost ms-shadow"></i>', ""
            )

        temp_rarity = card_details.find("small").contents[-1]
        temp_rarity = temp_rarity.strip()
        if temp_rarity == "Common":
            self.rarity = Rarity.COMMON
        elif temp_rarity == "Uncommon":
            self.rarity = Rarity.UNCOMMON
        elif temp_rarity == "Rare":
            self.rarity = Rarity.RARE
        elif temp_rarity == "Mythic Rare":
            self.rarity = Rarity.MYTHIC_RARE
        else:
            self.rarity = Rarity.UNKNOWN

    def __str__(self):
        return f"\n\t{self.title} --> {self.set}"


if __name__ == "__main__":
    pass
