from sets import MTG_Set, sets
from card import Card
import requests
from bs4 import BeautifulSoup

def gather_cards():
    sets_list=[]
    for card_set in sets:
        temp = MTG_Set(card_set)
        sets_list.append(temp)
        req = requests.get(temp.url)
        soup = BeautifulSoup(req.content, "html.parser")
        cards=soup.find('div', id='cards')
        card_list=cards.find_all('a',class_='item ae-card-link cardLink')
        for card in card_list:
            temp.cards.append(Card(card, temp))
    return sets_list

if __name__=="__main__":
    all_cards = gather_cards()
    for each in all_cards:
        print(each.display())