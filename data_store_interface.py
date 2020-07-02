import abc

class DataStoreInterface(abc.ABC):
    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def set(self):
        pass

    @abc.abstractmethod
    def clear(self):
        pass