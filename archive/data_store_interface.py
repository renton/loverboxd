import abc

class DataStoreInterface(abc.ABC):
    @abc.abstractmethod
    def get(self, datatype, id, cb=None):
        pass

    @abc.abstractmethod
    def set(self, datatype, id, value):
        pass

    @abc.abstractmethod
    def clear_key(self, key):
        pass

    @abc.abstractmethod
    def clear_all(self):
        pass