import abc

class LetterboxdDataObject(abc.ABC):
    datatype = 'obj'

    def __init__(self, id, data):
        self.id = id
        self._hydrate(data)      

    def _hydrate(self, data):
        for k,v in data.items():
            setattr(self, k, v)

    def save(self, ds):
        ds.set(self.__class__.datatype, self.id, vars(self))