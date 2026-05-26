import time
import threading


class SlidingWindowCounter:
    def __init__(self, capacity, window_size, clock):
        self.capacity = capacity
        self.window_size = window_size
        self.clock = clock

        self.current_window_start = clock.now()
        self.current_count = 0
        self.previous_count = 0

        self._lock = threading.Lock()

    def allow_request(self):
        with self._lock:
            now = self.clock.now()
            elapsed = now - self.current_window_start

            if elapsed >= self.window_size:
                windows_passed = int(elapsed // self.window_size)
                if windows_passed == 1:
                    self.previous_count = self.current_count
                else:
                    self.previous_count = 0

                self.current_count = 0
                self.current_window_start += windows_passed * self.window_size
                elapsed = now - self.current_window_start

            weighted_count = (
                self.current_count + self.previous_count * (1 - elapsed / self.window_size)
            )

            if weighted_count >= self.capacity:
                return False

            self.current_count += 1
            return True

class FakeClock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def advance(self, dt):
        self.t += dt


if __name__ == "__main__":
    clock = FakeClock()
    rate_limiter = SlidingWindowCounter(capacity=5, window_size=1, clock=clock)
    for _ in range(6):
        if rate_limiter.allow_request():
            print("Request SUCCEEDED!!")
        else:
            print("FAILED...")
    print('---')

    clock.advance(1.5)
    for _ in range(5):
        if rate_limiter.allow_request():
            print("Request SUCCEEDED!!")
        else:
            print("FAILED...")
