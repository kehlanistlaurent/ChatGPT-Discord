import redis
import json

class Memory:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)

    async def get(self, user_id):
        data = self.redis.get(user_id)
        if data:
            return json.loads(data)
        return []

    async def save(self, user_id, key, value):
        self.redis.set(user_id, json.dumps(value))

    async def delete(self, user_id):
        self.redis.delete(user_id)
