from letterboxd_data_object import LetterboxdDataObject

class Film(LetterboxdDataObject):
    datatype = 'films'

    def __init__(self, id, data):
        self.highest_rating_to_use = 10
        super().__init__(id, data)

    def __str__(self):
        return f"<Film: { self.id}>"