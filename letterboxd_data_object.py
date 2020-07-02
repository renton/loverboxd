import abc

DS_FILM_KEY = 'films'

class LetterboxdDataObject(abc.ABC):
    def __init__(self, data):
        self._hydrate(data)

    def _hydrate(self, data):
        for k,v in data.items():
            setattr(self, k, v)

    def save(self, ds):
        ds.set(DS_FILM_KEY, self.id, self)