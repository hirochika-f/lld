from bisect import insort

class EventStore:
    def __init__(self):
        self.events = []

    def append(self, event_id: str, timestamp: int):
        # O(N); N = len(self.events)
        insort(self.events, (timestamp, event_id))

    def get_latest(self, n: int):
        # O(n)
        return [e[1] for e in self.events[::-1][:n]]


if __name__ == "__main__":
    store = EventStore()
    store.append("event1", 100)
    store.append("event2", 200)
    store.append("event3", 150)
    store.append("event4", 50)
    store.append("event5", 250)
    print(store.get_latest(3))

