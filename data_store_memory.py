import hashlib
from collections import defaultdict
from data_store_interface import DataStoreInterface

DATA_TYPES = [ 'films', 'users' ]

class DataStoreMemory(DataStoreInterface):
    def __init__(self):
        self.data = {}
        for datatype in DATA_TYPES:            
            self.data[datatype] = defaultdict(lambda: None)
   
    def get(self, datatype, id, cb=None):
        if self.data[datatype][id]:
            print('---CACHE HIT--- ', id, hashlib.md5(self.data[datatype][id]).hexdigest())
            return self.data[datatype][id]
        else:
            print('>>>CACHE MISS>>> ', id)
            if (cb):
                get_data = cb()
                self.set(datatype, id, get_data)
                return get_data
            return None
    
    def set(self, datatype, id, value):
        self.data[datatype][id] = value

    def clear_key(self, key):
        pass

    def clear_all(self):
        pass