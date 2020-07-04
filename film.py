from letterboxd_data_object import LetterboxdDataObject

class Film(LetterboxdDataObject):
    def __init__(self, data):
        super().__init__(data)
        self.datatype = 'films'    

    def __str__(self):
        return f"<Film: { self.name}>"

    def save(self, ds):
        ds.set(self.datatype, self.id, self.user_watches)