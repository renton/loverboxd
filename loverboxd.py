import csv
import urllib.request
from bs4 import BeautifulSoup
from functools import reduce

from data_store_redis import DataStoreRedis
from letterboxd_scraper import LetterboxdScraper

MINIMUM_NUMBER_MATCHES = 5

class Loverboxd:
    def __init__(self):
        self.api = LetterboxdScraper( DataStoreRedis() )
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

    def get_recs_based_on_films(self, film_ids):
        film_recs = {}        

        my_films = {}
        if self.current_user:
            my_films = self.api.get_films_for_user(self.current_user, highest_rating_to_use=None)
   
        ratings = []
        for film_id in film_ids:
            ratings = ratings + list(self.api.get_ratings_for_film(film_id).values())
        total_users = len(ratings)
        
        # TODO double counting users that appear more than once. is this actually desirable?
        for rating in ratings:
            if rating['user_id'] != self.current_user:
                for user_film in self.api.get_films_for_user(rating['user_id']).values():
                    if user_film['film_id'] not in my_films:
                        if user_film['film_id'] not in film_recs:
                            film_recs[user_film['film_id']] = {
                                'count' : 0,
                            }

                        film_recs[user_film['film_id']]['count'] += 1

        rec_count = 0
        with open(f"{self.current_user}.csv", mode='w') as rec_file:
            rec_writer = csv.writer(rec_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for k,v in film_recs.items():
                if v['count'] >= MINIMUM_NUMBER_MATCHES:
                    rec_count += 1
                    rec_writer.writerow([v['count'], k])
        print('=======================')
        print('DONE! Films Recommended: ', rec_count)

if __name__ == "__main__":
    lbd = Loverboxd()
    lbd.set_user('hell0keekee')
    lbd.get_recs_based_on_films(
        [
            '/film/house',
            '/film/the-umbrellas-of-cherbourg',
            '/film/one-cut-of-the-dead',
            '/film/tampopo',
            '/film/3-women',
            '/film/out-of-the-blue',
            '/film/one-sings-the-other-doesnt',
            '/film/nowhere',
            '/film/good-time',
            '/film/bamboozled',
        ]
    )