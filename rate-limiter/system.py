import time
import threading

class TokenBucket:
    def __init__(self, capacity: int, rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.rate = rate
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        added_tokens = elapsed * self.rate
        self.tokens = min(self.tokens + added_tokens, self.capacity)
        self.last_refill = now

    def allow_request(self):
        with self._lock:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

class RateLimiter:
    def __init__(self, capacity: int, rate: float):
        self.capacity = capacity
        self.rate = rate
        self.user_buckets = {}
        self._lock = threading.Lock()

    def allow_request(self, user_id: str):
        with self._lock:
            if user_id not in self.user_buckets:
                self.user_buckets[user_id] = TokenBucket(self.capacity, self.rate)
            bucket = self.user_buckets[user_id]
            return bucket.allow_request()


if __name__ == "__main__":
    rate_limiter = RateLimiter(capacity=10, rate=2)
    for _ in range(5):
        if rate_limiter.allow_request("UserA"):
            print("Request SUCCEEDED!!")
        else:
            print("FAILED...")
    print("--- UserA 1st Requests DONE ---")

    for _ in range(10):
        if rate_limiter.allow_request("UserA"):
            print("Request SUCCEEDED!!")
        else:
            print("FAILED...")
    print("--- UserA Requests DONE ---")

    for _ in range(11):
        if rate_limiter.allow_request("UserB"):
            print("Request SUCCEEDED!!")
        else:
            print("FAILED...")
    print("--- UserB Requests DONE ---")
