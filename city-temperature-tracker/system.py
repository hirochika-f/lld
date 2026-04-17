from collections import defaultdict

def group_by_city(temperatures: list[str]) -> list[str]:
    d = defaultdict(list)
    for city_temp in temperatures:
        try:
            city, temp = city_temp.split(":")
            if not city or not temp:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid format: {city_temp}")
        d[city].append(int(temp))
    ret = []
    for city, temps in sorted(d.items()):
        ret.append(f"{city}:{','.join(str(t) for t in temps)}")
    return ret


if __name__ == "__main__":
    temperatures = ["JPN:32", "JPN:30", "AUS:18", "JPN:20"]
    ret = group_by_city(temperatures)
    print(ret)
