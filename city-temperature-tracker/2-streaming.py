from collections import defaultdict

class CityTemperatureTracker:
    def __init__(self):
        self.d = defaultdict(list)
        self.highest = defaultdict(lambda: float('-inf'))

    def ingest(self, entry: str) -> None:
        try:
            city, temp = entry.split(":")
            if not city or not temp:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid entry: {entry}")
        temp = int(temp)
        self.d[city].append(temp)
        self.highest[city] = max(self.highest[city], temp)

    def snapshot(self) -> list[str]:
        ret = []
        for city, temps in sorted(self.d.items()):
            ret.append(f"{city}:{','.join(str(t) for t in temps)}")
        return ret

    def get_latest(self, city: str) -> int:
        temps = self.d.get(city)
        if not temps:
            raise ValueError(f"Invalid city: {city}")
        return temps[-1]

    def get_highest(self, city: str) -> int:
        if city not in self.highest:
            raise ValueError(f"Invalid city: {city}")
        return self.highest[city]
        

if __name__ == "__main__":
    tracker = CityTemperatureTracker()
    temperatures = ["JPN:32", "JPN:30", "AUS:18", "JPN:20"]
    for temp in temperatures:
        tracker.ingest(temp)
    print(tracker.snapshot())
    print(tracker.get_latest("JPN"))
    print(tracker.get_highest("JPN"))
