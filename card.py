from enums import Type, Rarity, Color
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://aetherhub.com"
SET_URL = BASE_URL + "/Card/Set"
color_dict = {"ms-r":"RED",
              "ms-u":"BLUE",
              "ms-w":"WHITE",
              "ms-b":"BLACK",
              "ms-g":"GREEN",
              "ms-x":"VARIABLE"}
for x in range(20):
    color_dict[f"ms-{x}"]="COLORLESS"

class Card:
    def __init__(self, html_set):
        self.html_set=html_set
        self.title = self.html_set.find('div', class_="item-hidden-text").contents[0]
        self.url=BASE_URL + self.html_set.get('href')
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        temp = self.soup.find('div',id="cardInfo")
        self.img_url = temp.find('img')['src']
        # print(temp.prettify())
        self.card_details=temp.find('div',class_="col-sm-12 col-md-6 mt-3 mt-md-0")
        temp_colors = self.card_details.find('span', class_="pull-right")
        cost = temp_colors.find_all('i')
        self.mana_cost = dict()
        for item in cost:
            temp2 = item.get('class')[1]
            if temp2 in color_dict.keys():
                cost_color=color_dict[temp2]
            else:
                break
            if cost_color=="COLORLESS":
                self.mana_cost[cost_color] = int(temp2[3:])
            elif cost_color in self.mana_cost.keys():
                self.mana_cost[cost_color]+=1
            else:
                self.mana_cost[cost_color]=1
        self.color = 0
        if len(cost) != 0:
            for colorcosts in self.mana_cost.keys():
                self.color += Color[colorcosts]
        
        print(f"Color {self.color:05b} -->",self.mana_cost)

            
        # TODO: Anything below needs processed
        self.type = Type.Creatures
        self.subtype = ""
        self.power = 0
        self.toughness = 0
        self.abilities = []
        self.description = ""
        self.quote = ""
        self.rarity = Rarity.COMMON
        self.foil = False
        self.set = ""
        self.border_color="black"

    def __str__(self):
        return f"\n\t{self.title} --> {self.url}"