from letterboxd_data_object import LetterboxdDataObject

class Film(LetterboxdDataObject):
    def __init__(self, data):
        self.user_ratings = {}
        super().__init__(data)

    def __str__(self):
        return f"<Film: { self.name}>"