import requests
from bs4 import BeautifulSoup

BASE_URL = "https://aetherhub.com"
SET_URL = BASE_URL + "/Card/Set"

resp = requests.get(SET_URL)
soup = BeautifulSoup(resp.content, "html.parser")

table = soup.find('table', class_="table bg-ae-dark table-sm")
body = table.find('tbody')
sets = body.find_all('tr')

class MTG_Set:
    def __init__(self, content):
        self.release_date = content.find_all('td')[-1].contents[0]
        self.title = content.find('b').contents[0]
        self.shortened = content.find('small').contents[0]
        self.url = SET_URL + f"/{self.shortened}"

    def __str__(self):
        return f"{self.title}({self.shortened})"
    
    def display(self):
        return f"{self.title:<50} ({self.shortened}){' ' * (7-len(self.shortened))} \tReleased: {self.release_date}{(''.join(f'{x}'for x in self.cards))}"
    

