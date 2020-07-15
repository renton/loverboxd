from letterboxd_data_object import LetterboxdDataObject

class List(LetterboxdDataObject):
    datatype = 'lists'

    def __init__(self, id, data):
        super().__init__(id, data)
    
    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id