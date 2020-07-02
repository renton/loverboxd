import abc
from data_store_memory import DataStoreMemory

class LetterboxdAPIInterface(abc.ABC):
    def __init__(self, ds):
        self.ds = ds

    def get_films_for_user(self, use_id, bypass_data_store=False):        
        pass

    @abc.abstractmethod
    def get_watchlist_films_for_user(self, user_id, bypass_data_store=False):
        pass

    def get_user_ratings_for_film(self, film_id, bypass_data_store=False):
        pass