from collections import deque
import time


class RateLimitResult:
    def __init__(self, allowed: bool, remaining: int, retry_after_s: float):
        self.allowed = allowed
        self.remaining = remaining
        self.retry_after_s = retry_after_s


class Limiter:
    def __init__(self, algo_config: dict[str, str]):
        pass

    def allow_request(self, user_id: str):
        pass
 

class RateLimiter:
    def __init__(self, configs: list[dict[str, str]], default_config: dict[str, str]):
        self.limiters = {}
        for config in configs:
            self.limiters[config["endpoint"]] = self._create_limiter(config)
        self.default_limiter = self._create_limiter(default_config)

    def _create_limiter(self, config: dict[str, str]) -> Limiter:
        algorithm = config["algorithm"]
        if algorithm == "TokenBucket":
            return TokenBucketLimiter(config["algoConfig"])
        elif algorithm == "SlidingWindowLog":
            return SlidingWindowLogLimiter(config["algoConfig"])
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def allow_request(self, user_id, endpoint_name) -> RateLimitResult:
        if endpoint_name not in self.limiters:
            limiter = self.default_limiter
        else:
            limiter = self.limiters[endpoint_name]
        return limiter.allow_request(user_id)
      

class TokenBucketLimiter(Limiter):
    def __init__(self, algo_config: dict[str, str]):
        self.capacity = algo_config["capacity"]
        self.rate = algo_config["refillRatePerSecond"]
        self.buckets = {}

    def allow_request(self, user_id: str):
        if user_id not in self.buckets:
            self.buckets[user_id] = TokenBucket(self.capacity, self.rate)
        bucket = self.buckets[user_id]
        bucket.refill()
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return RateLimitResult(True, bucket.tokens, None)
        else:
            retry_time = (1 - bucket.tokens) / self.rate
            return RateLimitResult(False, 0, retry_time)


class TokenBucket:
    def __init__(self, capacity: int, rate: int):
        self.capacity = capacity
        self.tokens = capacity
        self.rate = rate
        self.last_refill_time = time.time()

    def refill(self):
        now = time.time()
        elapsed = (now - self.last_refill_time) * self.rate
        self.tokens = min(self.capacity, self.tokens + elapsed)
        self.last_refill_time = now
 

class SlidingWindowLogLimiter(Limiter):
    def __init__(self, algo_config: dict[str, str]):
        self.max_requests = algo_config["maxRequests"]
        self.window_s = algo_config["windowS"]
        self.logs = {}

    def allow_request(self, user_id):
        if user_id not in self.logs:
            self.logs[user_id] = deque()
        logs = self.logs[user_id]
        now = time.time()
        cutoff_time = now - self.window_s
        while logs and logs[0] < cutoff_time:
            logs.popleft()

        if len(logs) < self.max_requests:
            logs.append(now)
            remaining = self.max_requests - len(logs)
            return RateLimitResult(True, remaining, None)
        else:
            oldest_log = logs[0]
            retry_after_s = oldest_log + self.window_s - now
            return RateLimitResult(False, 0, retry_after_s)


if __name__ == "__main__":
    configs = [{
        "endpoint": "/v1/chat/completion",
        "algorithm": "TokenBucket",
        "algoConfig":{ 
            "capacity": 3,
            "refillRatePerSecond": 1
        }
    }]
    default_config = {
        "algorithm": "SlidingWindowLog",
        "algoConfig":{ 
            "maxRequests": 3,
            "windowS": 5
        }
    }


    limiter = RateLimiter(configs, default_config)
    for _ in range(10):
        result = limiter.allow_request("user", "/v1/chat/completion")
        print(result.allowed, result.remaining, result.retry_after_s)
    for _ in range(10):
        result = limiter.allow_request("user", "/v1/chat/streamCompletion")
        print(result.allowed, result.remaining, result.retry_after_s)

