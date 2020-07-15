import csv
import urllib.request
from bs4 import BeautifulSoup
from functools import reduce
from collections import defaultdict

from data_store_redis import DataStoreRedis
from letterboxd_scraper import LetterboxdScraper

MINIMUM_NUMBER_MATCHES_PERCENT = 0.20
MINIMUM_NUMBER_MATCHES_DEFAULT = 5

MINIMUM_NUMBER_MATCHES_SIMILAR_USERS = 15

HIGHEST_RATING_TO_USE = 9

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

    def find_similar_users(self):        
        # TODO Users that appear the most are highest match
        # TODO later: take all your film 1-10 ratings and apply a delta weight
        # TODO less popular films get a boost?
        user_recs = defaultdict(lambda: 0)

        my_films = {}
        if self.current_user:
            my_films = self.api.get_films_for_user(self.current_user, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=True)

        for k2,v2 in my_films.items():
            for k,v in self.api.get_ratings_for_film(k2).items():
                user_recs[k] += 1

        for k,v in user_recs.items():
            if v >= MINIMUM_NUMBER_MATCHES_SIMILAR_USERS:
                print(f"{k},{v}")
        return user_recs

    def user_compatibility_score(self, user1, user2):
        # TODO score based on deltas??
        # TODO normalize ratings??
        # TODO show the outliers??
        # TODO less popular films get a boost?
        user1_ratings = self.api.get_films_for_user(user1, highest_rating_to_use=None, bypass_cache=True)
        user2_ratings = self.api.get_films_for_user(user2, highest_rating_to_use=None, bypass_cache=True)

        shared_films = 0
        delta_matrix = defaultdict(lambda: 0)
        for k,v in user1_ratings.items():
            if k in user2_ratings:
                if v['rating'] and user2_ratings[k]['rating']:
                    delta = abs(v['rating'] - user2_ratings[k]['rating'])
                    delta_matrix[delta] += 1
                    shared_films += 1                

        print('Shared Films: ', shared_films)
        for k,v in delta_matrix.items():
            perc = "{:.2f}".format((v / shared_films) * 100)
            print(f"{k}: {v} ({perc}%)")

        score = 0
        for k,v in delta_matrix.items():
            score += abs(10 - k) * v
        score = "{:.2f}".format( score / shared_films )
        print(score)

    def get_recs_based_on_films(self, film_ids):
        film_recs = {}

        my_films = {}
        if self.current_user:
            my_films = self.api.get_films_for_user(self.current_user, highest_rating_to_use=None, bypass_cache=True)
   
        ratings = defaultdict(lambda: 0)
        for film_id in film_ids:
            for rating in self.api.get_ratings_for_film(film_id).user_watches.values():
                ratings[rating['user_id']] += 1

        total_users = len(ratings.keys())
        min_number_matches = max(MINIMUM_NUMBER_MATCHES_DEFAULT, len(film_ids) * MINIMUM_NUMBER_MATCHES_PERCENT)
        remove_users = [k for k in ratings if ratings[k] < min_number_matches]
        for k in remove_users: del ratings[k]
       
        for user_id in ratings.keys():
            if user_id != self.current_user:
                for user_film in self.api.get_films_for_user(user_id, highest_rating_to_use=HIGHEST_RATING_TO_USE, bypass_cache=False).watched_films.values():
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
                rec_count += 1
                rec_writer.writerow([v['count'], k])
        print('=======================')
        print(f"Checked against {len(film_ids)} films")
        print(f"Matched Users (at least {min_number_matches} matches): {len(ratings.keys())} / {total_users}")
        print('DONE! Films Recommended: ', rec_count)

if __name__ == "__main__":
    lbd = Loverboxd()
    lbd.set_user('rentonl')
    #films = list(lbd.api.get_films_for_user(lbd.current_user, highest_rating_to_use=8, bypass_cache=True).watched_films.keys())
    x = lbd.api.get_ratings_for_film('/film/breathless/', highest_rating_to_use=10, bypass_cache=False)
    print(vars(x).keys())
    #print(films)
    #lbd.find_similar_users()
    #lbd.user_compatibility_score('rrinehart1976', 'rentonl')
    #lbd.get_recs_based_on_films(films)