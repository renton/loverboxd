import abc
import urllib.request
from bs4 import BeautifulSoup
from functools import reduce

from data_store_memory import DataStoreMemory
from letterboxd_scraper import LetterboxdScraper

class Loverboxd:
    def __init__(self):
        self.api = LetterboxdScraper( DataStoreMemory() )
        self.current_user = None

    def set_user(self, current_user):
        self.current_user = current_user

    def find_shared_watchlisted_films_for_users(self, user_ids):
        films = []

        for user_id in user_ids:
            films.append(self.api.get_watchlist_films_for_user(user_id).keys())
        
        matches = list(reduce(set.intersection, [set(item) for item in films ]))

    def get_ratings_for_film(self, film_id):
        return self.api.get_ratings_for_film(film_id)

    def get_films_for_user(self, user_id):
        return self.api.get_films_for_user(user_id)

    def get_recs_based_on_film(self, film_id):
        # TODO filter out your own - get all current users films
        # TODO filter out films you've seen
        film_recs = {}
        ratings = self.api.get_ratings_for_film(film_id).values()
        total_users = len(ratings)
        
        for rating in ratings:
            if rating.user_id != self.current_user:
                for user_film in self.api.get_films_for_user(rating.user_id).values():
                    if user_film.film_id not in film_recs:
                        film_recs[user_film.film_id] = {
                            'avg' : None,
                            'count' : None,
                            'ratings' : [],
                        }

                    film_recs[user_film.film_id]['ratings'].append(user_film.rating)

        print('-----')
        for k,v in film_recs.items():
            v['avg'] = sum(v['ratings']) / len(v['ratings'])
            v['count'] = len(v['ratings'])
            if v['count'] > ( total_users * 0.1 ):
                print(v['count'], v['avg'], k)

if __name__ == "__main__":
    lbd = Loverboxd()
    lbd.set_user('rentonl')
    print(lbd.get_recs_based_on_film('/film/fist-of-the-north-star'))