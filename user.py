class User(LetterboxdDataObject):
    def __init__(self):
        self.id = 'boop'
        self.watched_films = {}
        self.wishlisted_films = {}