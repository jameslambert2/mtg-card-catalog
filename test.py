import requests
from bs4 import BeautifulSoup
from card import Card, SET_URL

resp = requests.get(SET_URL)
soup = BeautifulSoup(resp.content, "html.parser")
# print(soup.prettify())

table = soup.find('table', class_="table bg-ae-dark table-sm")
body = table.find('tbody')
sets = body.find_all('tr')

class MTG_Set:
    def __init__(self, content):
        self.release_date = content.find_all('td')[-1].contents[0]
        self.title = content.find('b').contents[0]
        self.shortened = content.find('small').contents[0]
        self.url = SET_URL + f"/{self.shortened}"
        self.cards = []

    def __str__(self):
        return f"{self.title:<50} ({self.shortened}){' ' * (7-len(self.shortened))} \tReleased: {self.release_date}{(''.join(f'{x}'for x in self.cards))}"

sets_list=[]
skip=True
for card_set in sets:
    if skip:
        skip=False
        continue
    temp = MTG_Set(card_set)
    sets_list.append(temp)
    req = requests.get(temp.url)
    soup = BeautifulSoup(req.content, "html.parser")
    cards=soup.find('div', id='cards')
    card_list=cards.find_all('a',class_='item ae-card-link cardLink')
    for card in card_list:
        temp.cards.append(Card(card))
        # break # Temporary to check 1 card
    # print(temp)
    break # TEMPORARY STOP SO I DON'T PULL 90000 CARDS EVERY RUN

# temp_rel_date = sets[0].find_all('td')[-1].contents[0]
# temp_name = sets[0].find('b')
# temp_shortened = sets[0].find('small')
# print(temp_name.contents[0], temp_shortened.contents[0], " \tReleased: ", temp_rel_date)

# card_body = soup.find('div', class_='card-body')
# title = card_body.find('h2').contents[0]
# type = card_body.find_all('p')
# print(title)
# i=0
# while True:
#     try:
#         print(type[i])
#         i+=1
#     except IndexError:
#         break