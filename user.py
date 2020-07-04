from letterboxd_data_object import LetterboxdDataObject

class User(LetterboxdDataObject):
    def __init__(self, data):
        super().__init__(data)
        self.datatype = 'users'
    
    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def save(self, ds):
        ds.set(self.datatype, self.id, self.watched_films)