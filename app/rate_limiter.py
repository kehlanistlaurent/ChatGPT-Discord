import time

class RateLimiter:
    def __init__(self):
        self.last_called = {}

    def is_allowed(self, user_id, cooldown=2):
        now = time.time()
        if user_id in self.last_called:
            if now - self.last_called[user_id] < cooldown:
                return False
        self.last_called[user_id] = now
        return True
