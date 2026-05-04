import os
import redis
import time
import json

class RedisCache:
    def __init__(self):
        host = os.environ.get("REDIS_HOST", "localhost")
        self.r = redis.Redis(host=host, port=6379, decode_responses=True)

    def getLastCacheTime(self, name):
        for cache in self.r.keys():
            if name in cache:
                pass

    def write(self, name, data):
        constructName = f"{name}_{int(time.time())}"
        self.r.set(constructName, json.dumps(data))

    def readStr(self, name):
        data = self.r.get(name)
        if data:
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return None
    
    def readAll(self, name):
        data = self.r.get(name)
        if data:
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return None
    
    def close(self):
        self.r.close()
