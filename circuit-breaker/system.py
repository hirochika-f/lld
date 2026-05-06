import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=3, half_open_success_threshold=2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_success_threshold = half_open_success_threshold

        self.state = State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        now = time.time()

        if self.state == State.OPEN:
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = State.HALF_OPEN
                print("# STATE CHANGED --> HALF_OPEN")
            else:
                raise Exception("Circuit is OPEN")

        try:
            result = func(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise
        else:
            self._on_success()
            return result

    def _on_failure(self):
        self.failure_count += 1
        
        if self.state == State.HALF_OPEN:
            self._trip()
        elif self.failure_count >= self.failure_threshold:
            self._trip()

    def _on_success(self):
        if self.state == State.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self._reset()
        else:
            self.failure_count = 0

    def _trip(self):
        print("# STATE CHANGED --> OPEN")
        self.state = State.OPEN
        self.last_failure_time = time.time()
        self.failure_count = 0
        self.success_count = 0

    def _reset(self):
        print("# STATE CHANGED --> CLOSED")
        self.state = State.CLOSED
        self.failure_count = 0
        self.success_count = 0


if __name__ == "__main__":
    def unstable():
        raise Exception("fail")

    def stable():
        return "success"

    cb = CircuitBreaker()

    for _ in range(5):
        try:
            ret = cb.call(stable)
            print(cb.state, ret)
        except Exception as e:
            print(cb.state, e)

    for _ in range(5):
        try:
            ret = cb.call(unstable)
            print(cb.state, ret)
        except Exception as e:
            print(cb.state, e)

    # wait to change half open state
    time.sleep(5)
    for _ in range(2):
        try:
            ret = cb.call(stable)
            print(cb.state, ret)
        except Exception as e:
            print(cb.state, e)
            time.sleep(1)

