"""
sets.py

Created by: James Lambert
Last Updated: 11 Aug 2025

Creation for Set Lookup
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://aetherhub.com"
SET_URL = BASE_URL + "/Card/Set"

try:
    RESPONSE = requests.get(SET_URL, timeout=5)
except TimeoutError:
    RESPONSE = None

if RESPONSE:
    soup = BeautifulSoup(RESPONSE.content, "html.parser")

    table = soup.find("table", class_="table bg-ae-dark table-sm")
    body = table.find("tbody")
    sets = body.find_all("tr")


class MTGSet:
    """
    MTGSet object containing the Set information for the database lookup functionality

    Args:
        content: requests._AtMostOneElement - Results from find function
    """
    def __init__(self, content):
        self.release_date = content.find_all("td")[-1].contents[0]
        self.title = content.find("b").contents[0]
        self.shortened = content.find("small").contents[0]
        self.url = SET_URL + f"/{self.shortened}"

    def __str__(self):
        return f"{self.title}({self.shortened})"

    def display(self):
        """MTGSet Display function

        Display the contents in the MTGSet object in a semi-structured format
        
        """
        return (f"{self.title:<50} ({self.shortened}){' ' * (7-len(self.shortened))}",
            f"\tReleased: {self.release_date}")
