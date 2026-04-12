from bisect import insort

class EventStore:
    def __init__(self):
        self.events = []

    def append(self, event_id: str, timestamp: int):
        # O(n)
        insort(self.events, (timestamp, event_id))

    def get_latest(self, n: int):
        # O(n)
        return [e[1] for e in reversed(self.events[-n:])]


if __name__ == "__main__":
    store = EventStore()
    store.append("event1", 100)
    store.append("event2", 200)
    store.append("event3", 150)
    print(store.get_latest(2))

