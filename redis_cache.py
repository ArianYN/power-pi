import os
import redis
import time
import json
from logger import Log

class RedisCache:
    def __init__(self):
        host = os.environ.get("REDIS_HOST", "localhost")
        self.r = redis.Redis(host=host, port=6379, decode_responses=True)
        self.logger = Log()

    def _findKey(self, name):
        for cache in self.r.keys():
            if name in cache:
                return cache
        return None

    def getLastCacheTime(self, name):
        self.logger.log_info(f"All Redis Keys: {self.r.keys()}", True)

        cache = self._findKey(name)
        
        if cache != None:
            return int(cache.split("_")[1])
        
        return 0

    def write(self, name, data):
        constructName = f"{name}_{int(time.time())}"

        cacheToDelete = self._findKey(name)

        if cacheToDelete != None:
            self.r.delete(cacheToDelete)

        self.r.set(constructName, json.dumps(data))

    def readStr(self, name):
        key = self._findKey(name)
        if key:
            data = self.r.get(key)
            if data:
                try:
                    return json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    return data
        return None
    
    def readAll(self, name):
        key = self._findKey(name)
        if key:
            data = self.r.get(key)
            if data:
                try:
                    return json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    return data
        return None
    
    def close(self):
        self.r.close()
