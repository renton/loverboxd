import abc

class LetterboxdDataObject(abc.ABC):
    def __init__(self, data):
        self._hydrate(data)
        self.datatype = 'obj'

    def _hydrate(self, data):
        for k,v in data.items():
            setattr(self, k, v)

    def save(self, ds):
        ds.set(self.datatype, self.id, None)