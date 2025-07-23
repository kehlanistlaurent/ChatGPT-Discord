import time

_last_call = 0
RATE_LIMIT_SECONDS = 1.5  # Adjust if needed

def rate_limit():
    """
    Simple rate limiter to avoid hitting API too quickly.
    """
    global _last_call
    now = time.time()
    elapsed = now - _last_call
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)
    _last_call = time.time()
