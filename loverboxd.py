import abc
import urllib.request
from bs4 import BeautifulSoup
from functools import reduce

from data_store_memory import DataStoreMemory
from letterboxd_scraper import LetterboxdScraper

class Loverboxd:
    def __init__(self):
        self.api = LetterboxdScraper( DataStoreMemory() )

    def find_shared_watchlisted_films_for_users(self, user_ids):
        films = []

        for user_id in user_ids:
            films.append(self.api.get_watchlist_films_for_user(user_id).keys())
        
        matches = list(reduce(set.intersection, [set(item) for item in films ]))

if __name__ == "__main__":
    lbd = Loverboxd()
    lbd.find_shared_watchlisted_films_for_users([])