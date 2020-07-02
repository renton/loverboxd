from letterboxd_data_object import LetterboxdDataObject

class WatchedFilm(LetterboxdDataObject):
    def __init__(self, data):
        # id user:film
        super().__init__(data)

    def __str__(self):
        return f"<({self.rating}) {self.user_id } : { self.film_id}>"

    def __repr__(self):
        return f"<({self.rating}) {self.user_id } : { self.film_id}>"
