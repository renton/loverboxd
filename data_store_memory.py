import hashlib
from collections import defaultdict
from data_store_interface import DataStoreInterface

DATA_TYPES = [ 'films', 'users', 'requests' ]

class DataStoreMemory(DataStoreInterface):
    def __init__(self):
        self.data = {}
        for datatype in DATA_TYPES:            
            self.data[datatype] = defaultdict(lambda: None)
   
    def get(self, datatype, id, cb):
        if self.data[datatype][id]:
            print('---CACHE HIT--- ', id, hashlib.md5(self.data[datatype][id]).hexdigest())
            return self.data[datatype][id]
        else:
            print('>>>CACHE MISS>>> ', id)
            get_data = cb()
            self.set(datatype, id, get_data)
            return get_data
    
    def set(self, datatype, id, value):
        self.data[datatype][id] = value

    def clear(self):
        self.data = {}