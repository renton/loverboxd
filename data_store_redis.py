import redis
import json
from data_store_interface import DataStoreInterface

class DataStoreRedis(DataStoreInterface):
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

    def get(self, datatype, id, cb=None):
        key = f"{datatype}:{id}"
        if self.redis.exists(key):
            value = self.redis.get(key)
            if value:
                print('>>>>> CACHE HIT', key)
                return json.loads(value)

        return None
    
    def set(self, datatype, id, value):
        key = f"{datatype}:{id}"
        self.redis.set(key, json.dumps(value))

    def clear_key(self, key):
        pass

    def clear_all(self):
        pass