import redis
import json
import os

class Memory:
    def __init__(self, redis_url=None):
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        try:
            self.redis = redis.from_url(redis_url)
            self.redis.ping()
            print(f"🧠 Connected to Redis at {redis_url}")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis = None

    async def get(self, user_id):
        if not self.redis:
            return {}
        data = self.redis.get(user_id)
        if data:
            return json.loads(data)
        return {}

    async def save(self, user_id, key, value):
        if not self.redis:
            return
        current = await self.get(user_id)
        current[key] = value
        self.redis.set(user_id, json.dumps(current))

    async def clear(self, user_id):
        if self.redis:
            self.redis.delete(user_id)

    async def mark_friend(self, user_id):
        if not self.redis:
            return
        current = await self.get(user_id)
        current["friend"] = True
        self.redis.set(user_id, json.dumps(current))
